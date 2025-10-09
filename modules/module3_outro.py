import asyncio
import aiohttp
import ssl
import cloudinary
import cloudinary.uploader
from pathlib import Path
from loguru import logger
from config import Config
from openai import OpenAI
from typing import Dict, Optional

class OutroGenerator:
    def __init__(self):
        try:
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {e}")
            self.openai_client = None
        self.config = Config
        # Initialize Cloudinary
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET
        )
    
    def _clean_trademark_symbols(self, script: str) -> str:
        """Remove trademark symbols and company references from script (except allkeyshop.com)"""
        import re
        
        # Remove trademark symbols
        trademark_symbols = ['™', '®', '©', 'TM', 'SM', '(TM)', '(R)', '(C)']
        for symbol in trademark_symbols:
            script = script.replace(symbol, '')
        
        # Remove common company/trademark patterns (but preserve allkeyshop.com)
        patterns_to_remove = [
            r'\b(Inc\.?|LLC|Ltd\.?|Corporation|Corp\.?)\b',  # Company suffixes
            r'\b(?!allkeyshop)(Studios?|Entertainment|Games?|Interactive)\b(?=\s|$)',  # Game company words (except allkeyshop)
            r'\bTrademark\b',  # The word "Trademark"
            r'\bAll rights reserved\b',  # Rights text
        ]
        
        for pattern in patterns_to_remove:
            script = re.sub(pattern, '', script, flags=re.IGNORECASE)
        
        # Clean up extra spaces and normalize
        script = ' '.join(script.split())
        
        logger.info(f"Cleaned outro script of trademark symbols: {script}")
        return script
        
    async def generate_outro_script(self, game_title: str, game_details: Dict = None) -> str:
        """Generate outro script using OpenAI"""
        try:
            logger.info(f"Generating outro script for {game_title}")
            
            # Clean game title of trademark symbols before using in script
            clean_game_title = self._clean_trademark_symbols(game_title)
            
            # Create context from game details
            context = f"Game: {clean_game_title}"
            if game_details:
                if game_details.get('release_date'):
                    context += f"\nRelease Date: {game_details['release_date']}"
                if game_details.get('developer'):
                    context += f"\nDeveloper: {game_details['developer']}"
            
            prompt = f"""
            Create a very short 8-second outro script for a YouTube Reel about the game "{clean_game_title}".
            
            Context:
            {context}
            
            Requirements:
            - Exactly 8 seconds when spoken (approximately 15-18 words maximum)
            - MUST include "allkeyshop.com - your games at the best price!"
            - Include a call-to-action (like, subscribe)
            - Use simple, direct language perfect for voice-over
            - No punctuation or complex sentences
            - EXCLUDE all trademarks, logos, and symbols (™, ®, ©, TM)
            - Do NOT include company names or trademark references beyond the required allkeyshop.com
            
            Example format: "Like and subscribe for more gaming! Visit allkeyshop.com - your games at the best price!"
            
            Script format: Just return the script text, no additional formatting.
            """
            
            if self.openai_client:
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a gaming content creator who writes engaging YouTube Reel outros with strong CTAs. NEVER include trademarks, logos, company names, or symbols like ™, ®, ©, TM beyond the required allkeyshop.com reference."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.8
                )
                script = response.choices[0].message.content.strip()
                
                # Clean any trademark symbols that might have appeared
                script = self._clean_trademark_symbols(script)
                
            else:
                logger.error("OpenAI API not available")
                raise Exception("OpenAI API is required for script generation")
            
            logger.info(f"Generated outro script: {script[:50]}...")
            return script
            
        except Exception as e:
            logger.error(f"Error generating outro script: {e}")
            raise Exception(f"OpenAI API failed for outro script generation: {e}")
    
    async def generate_heygen_video(self, script: str, game_title: str) -> Optional[str]:
        """Generate outro video using HeyGen API"""
        try:
            headers = {
                'X-Api-Key': Config.HEYGEN_API_KEY,
                'Content-Type': 'application/json'
            }
            
            # HeyGen template-based payload for outro - using updated template
            template_id = "537836c8f0264d38b22e1225ad6945b9"
            payload = {
                "test": True,  # Use test mode first
                "caption": False,
                "title": f"{game_title} Outro Video",
                "variables": {
                    "script": {
                        "name": "script",
                        "type": "text",
                        "properties": {
                            "content": script
                        }
                    }
                }
            }
            
            # Create SSL context that doesn't verify certificates (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Create video generation job using template
                async with session.post(
                    f"{Config.HEYGEN_BASE_URL}/template/{template_id}/generate",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        data = result.get('data', {})
                        video_id = data.get('video_id')
                        
                        if video_id:
                            # Poll for video completion and get URL from status endpoint
                            logger.info(f"Polling HeyGen status for outro video: {video_id}")
                            try:
                                video_url = await self._poll_heygen_status(session, headers, video_id)
                                if video_url:
                                    logger.info(f"✅ Got HeyGen outro video URL: {video_url}")
                                    # Download and upload to Cloudinary for better Creatomate compatibility
                                    cloudinary_url = await self._download_and_upload_video(session, video_url, game_title)
                                    return cloudinary_url
                                else:
                                    raise Exception("No video URL returned from HeyGen status endpoint")
                            except Exception as status_error:
                                logger.error(f"Status polling failed: {status_error}")
                                raise Exception(f"Failed to get outro video URL: {status_error}")
                        else:
                            raise Exception("HeyGen API returned no video ID")
                    else:
                        error_text = await response.text()
                        logger.error(f"HeyGen API error: {response.status} - {error_text}")
                        raise Exception(f"HeyGen API failed with status {response.status}: {error_text}")
            
        except Exception as e:
            logger.error(f"Error generating HeyGen outro video: {e}")
            raise Exception(f"HeyGen outro video generation failed: {e}")
    
    async def _poll_heygen_status(self, session: aiohttp.ClientSession, headers: Dict, video_id: str) -> Optional[str]:
        """Poll HeyGen API for video completion status"""
        max_attempts = 120  # 10 minutes with 5-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            try:
                async with session.get(
                    f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        data = result.get('data', {})
                        status = data.get('status')
                        
                        if status == 'completed':
                            # Fixed API endpoint parsing (from memory)
                            # CORRECTED: data.video_url (not data.result.video_url)
                            video_url = data.get('video_url')  # Direct from HeyGen API response
                            logger.info(f"HeyGen outro video completed: {video_url}")
                            return video_url
                        elif status == 'failed':
                            error_msg = data.get('error', 'Unknown error')
                            logger.error(f"HeyGen outro video generation failed: {error_msg}")
                            raise Exception(f"HeyGen outro video generation failed: {error_msg}")
                        else:
                            logger.info(f"HeyGen outro video status: {status}")
                
                await asyncio.sleep(5)
                attempt += 1
                
            except Exception as e:
                logger.error(f"Error polling HeyGen outro status: {e}")
                await asyncio.sleep(5)
                attempt += 1
        
        logger.error("HeyGen outro video generation timed out")
        raise Exception("HeyGen outro video generation timed out after 10 minutes")
    
    async def _download_and_upload_video(self, session: aiohttp.ClientSession, video_url: str, game_title: str) -> str:
        """Download HeyGen video and upload to Cloudinary"""
        try:
            # Clean filename
            safe_title = "".join(c for c in game_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_outro.mp4"
            
            # Ensure directory exists
            save_dir = Config.ASSETS_PATH / "outros"
            save_dir.mkdir(parents=True, exist_ok=True)
            output_path = save_dir / filename
            
            # Download video
            logger.info(f"Downloading outro video from: {video_url}")
            async with session.get(video_url) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', 'unknown')
                    content_length = response.headers.get('content-length', 'unknown')
                    logger.info(f"Downloaded content type: {content_type}, size: {content_length} bytes")
                    
                    with open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    logger.info(f"Downloaded outro video: {output_path}")
                    
                    # Upload to Cloudinary
                    cloudinary_url = await self._upload_to_cloudinary(str(output_path), f"outro_{safe_title}")
                    return cloudinary_url
                else:
                    raise Exception(f"Failed to download video: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Error downloading and uploading outro video: {e}")
            raise Exception(f"Outro video download/upload failed: {e}")
    
    async def _download_video(self, session: aiohttp.ClientSession, video_url: str, game_title: str, module_type: str) -> Optional[str]:
        """Download video from URL and save locally"""
        try:
            # Clean filename
            safe_title = "".join(c for c in game_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_{module_type}.mp4"
            output_path = Config.ASSETS_PATH / f"{module_type}s" / filename
            
            async with session.get(video_url) as response:
                if response.status == 200:
                    with open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    logger.info(f"Downloaded {module_type} video: {output_path}")
                    
                    # Upload to Cloudinary
                    cloudinary_url = await self._upload_to_cloudinary(str(output_path), f"{module_type}_{safe_title}")
                    logger.info(f"✅ Outro uploaded to Cloudinary: {cloudinary_url}")
                    return cloudinary_url
                else:
                    logger.error(f"Failed to download {module_type} video: {response.status}")
                    raise Exception(f"Failed to download {module_type} video: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Error downloading {module_type} video: {e}")
            raise Exception(f"{module_type} video download failed: {e}")
    
    async def _upload_to_cloudinary(self, file_path: str, public_id: str) -> str:
        """Upload video to Cloudinary and return URL"""
        try:
            logger.info(f"Uploading to Cloudinary: {file_path}")
            
            # Clean public_id to avoid URL encoding issues
            clean_public_id = public_id.replace(" ", "_").replace(":", "").replace("'", "").replace("%", "")
            
            # Upload video to Cloudinary with public access settings
            result = cloudinary.uploader.upload(
                file_path,
                resource_type="video",
                public_id=clean_public_id,
                folder="youtube_reels",
                overwrite=True,
                type="upload",
                access_mode="public",
                use_filename=False,
                unique_filename=True
            )
            
            cloudinary_url = result['secure_url']
            logger.info(f"✅ Uploaded to Cloudinary: {cloudinary_url}")
            return cloudinary_url
            
        except Exception as e:
            logger.error(f"Error uploading to Cloudinary: {e}")
            raise Exception(f"Cloudinary upload failed: {e}")
    
    async def create_outro(self, game_title: str, game_details: Dict = None) -> Optional[str]:
        """Main method to create outro video"""
        try:
            logger.info(f"Creating outro for {game_title}")
            
            # Generate script
            script = await self.generate_outro_script(game_title, game_details)
            
            # Generate video with HeyGen
            video_path = await self.generate_heygen_video(script, game_title)
            
            logger.info(f"Outro created successfully: {video_path}")
            return video_path
                
        except Exception as e:
            logger.error(f"Error creating outro: {e}")
            raise Exception(f"Outro creation failed: {e}")
    
    async def create_custom_outro(self, game_title: str, custom_message: str = None) -> Optional[str]:
        """Create outro with custom message"""
        try:
            if custom_message:
                script = custom_message
            else:
                script = await self.generate_outro_script(game_title)
            
            return await self.generate_heygen_video(script, game_title)
            
        except Exception as e:
            logger.error(f"Error creating custom outro: {e}")
            return None
