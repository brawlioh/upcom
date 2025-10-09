import asyncio
import aiohttp
import ssl
import cloudinary
import cloudinary.uploader
import os
import tempfile
import requests
import re
from pathlib import Path
from loguru import logger
from config import Config
from openai import OpenAI
from typing import Dict, Optional

class IntroGenerator:
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
        """Remove trademark symbols and company references from script"""
        import re
        
        # Remove trademark symbols
        trademark_symbols = ['™', '®', '©', 'TM', 'SM', '(TM)', '(R)', '(C)']
        for symbol in trademark_symbols:
            script = script.replace(symbol, '')
        
        # Remove common company/trademark patterns
        patterns_to_remove = [
            r'\b(Inc\.?|LLC|Ltd\.?|Corporation|Corp\.?)\b',  # Company suffixes
            r'\b(Studios?|Entertainment|Games?|Interactive)\b(?=\s|$)',  # Game company words
            r'\bTrademark\b',  # The word "Trademark"
            r'\bAll rights reserved\b',  # Rights text
        ]
        
        for pattern in patterns_to_remove:
            script = re.sub(pattern, '', script, flags=re.IGNORECASE)
        
        # Clean up extra spaces and normalize
        script = ' '.join(script.split())
        
        logger.info(f"Cleaned script of trademark symbols: {script}")
        return script
    
    async def generate_intro_script(self, game_title: str, game_details: Dict = None) -> str:
        """Generate intro script using OpenAI"""
        try:
            logger.info(f"Generating intro script for {game_title}")
            
            # Clean game title of trademark symbols before using in script
            clean_game_title = self._clean_trademark_symbols(game_title)
            
            # Build context from game details
            context = f"Game: {clean_game_title}"
            if game_details:
                if game_details.get('developer'):
                    context += f"\nDeveloper: {game_details['developer']}"
                if game_details.get('release_date'):
                    context += f"\nRelease Date: {game_details['release_date']}"
                if game_details.get('description'):
                    context += f"\nDescription: {game_details['description'][:200]}..."
                if game_details.get('genres'):
                    context += f"\nGenres: {', '.join(game_details['genres'][:3])}"
            
            # Extract and format release date for script context
            release_date_context = ""
            if game_details and game_details.get('release_date'):
                release_date = game_details['release_date']
                if release_date and release_date != "Unknown":
                    # Smart release date formatting for different formats
                    release_lower = release_date.lower()
                    
                    # Handle different date formats
                    if "2024" in release_date or "2025" in release_date or "2026" in release_date or "2027" in release_date:
                        # Future releases
                        if "coming soon" in release_lower or "tba" in release_lower:
                            release_date_context = "coming soon"
                        elif "q1" in release_lower or "q2" in release_lower or "q3" in release_lower or "q4" in release_lower:
                            release_date_context = f"dropping {release_date}"
                        elif "early access" in release_lower:
                            release_date_context = f"in early access {release_date}"
                        else:
                            release_date_context = f"releasing {release_date}"
                    elif "2023" in release_date or "2022" in release_date:
                        # Recent releases
                        release_date_context = f"now available since {release_date}"
                    else:
                        # Generic format
                        release_date_context = f"available {release_date}"

            prompt = f"""
            Create a short intro script for a YouTube Reel about the game "{clean_game_title}".
            
            Requirements:
            - Exactly 2 sentences
            - Each sentence should be 5-8 words
            - Energetic and engaging tone
            - Build excitement for the game
            - MUST include the release date if available: {release_date_context}
            - If no release date, focus on game excitement and features
            - Keep it under 15 seconds when spoken
            - Focus on upcoming releases and hype
            - EXCLUDE all trademarks, logos, and symbols (™, ®, ©, TM)
            - Do NOT include company names or trademark references
            - Focus only on the game title and gameplay features
            
            Examples with release dates: 
            - "{clean_game_title} drops this December! Get ready for epic adventures!"
            - "Coming 2025, {clean_game_title} changes everything! Prepare for the ultimate experience!"
            - "{clean_game_title} releases March 2024! This will blow your mind!"
            - "Mark your calendars now! {clean_game_title} {release_date_context}!"
            - "{clean_game_title} is {release_date_context}! Don't miss this incredible game!"
            - "Get hyped gamers! {clean_game_title} {release_date_context}!"
            
            Context: {context}
            
            Script format: Just return the script text, no additional formatting.
            """
            
            if self.openai_client:
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a gaming content creator who writes engaging, energetic intro scripts for YouTube Shorts about upcoming video games. Always include release dates when available to create urgency and excitement. Focus on upcoming releases and build hype. Keep it under 15 seconds when spoken. NEVER include trademarks, logos, company names, or symbols like ™, ®, ©, TM. Focus only on game titles and gameplay features."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=200,
                    temperature=0.8
                )
                script = response.choices[0].message.content.strip()
                
                # Clean any trademark symbols that might have appeared
                script = self._clean_trademark_symbols(script)
                
            else:
                logger.error("OpenAI API not available")
                raise Exception("OpenAI API is required for script generation")
            
            logger.info(f"Generated intro script: {script[:50]}...")
            return script
            
        except Exception as e:
            logger.error(f"Error generating intro script: {e}")
            raise Exception(f"OpenAI API failed for intro script generation: {e}")
    
    async def generate_heygen_video(self, script: str, game_title: str) -> Optional[str]:
        """Generate video using HeyGen API"""
        try:
            logger.info(f"Generating HeyGen video for {game_title}")
            headers = {
                'X-Api-Key': Config.HEYGEN_API_KEY,
                'Content-Type': 'application/json'
            }
            
            # HeyGen template-based payload - using updated template
            template_id = "537836c8f0264d38b22e1225ad6945b9"
            payload = {
                "test": True,  # Use test mode first
                "caption": False,
                "title": f"{game_title} Intro Video",
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
                            # Use official HeyGen API to download and upload to Cloudinary for Creatomate
                            logger.info(f"Using official HeyGen API to process video for Creatomate: {video_id}")
                            try:
                                # First try to get the video URL using the polling method
                                logger.info("Getting video URL using polling method...")
                                video_url = await self._poll_heygen_status(session, headers, video_id)
                                
                                if video_url and video_url.startswith('http'):
                                    logger.info(f"Got video URL from polling: {video_url}")
                                    # Download and upload to Cloudinary
                                    cloudinary_url = await self._download_video(session, video_url, game_title, "intro")
                                    if cloudinary_url:
                                        logger.info(f"✅ HeyGen video processed and uploaded to Cloudinary: {cloudinary_url}")
                                        return cloudinary_url
                                    else:
                                        raise Exception("Failed to download and upload video to Cloudinary")
                                else:
                                    raise Exception("Failed to get valid video URL from polling")
                                    
                            except Exception as download_error:
                                logger.error(f"Polling and download method failed: {download_error}")
                                raise Exception("HeyGen video processing failed - could not get video URL from status endpoint")
                        else:
                            raise Exception("HeyGen API returned no video ID")
                    else:
                        error_text = await response.text()
                        logger.error(f"HeyGen API error: {response.status} - {error_text}")
                        raise Exception(f"HeyGen API failed with status {response.status}: {error_text}")
            
        except Exception as e:
            logger.error(f"Error generating HeyGen video: {e}")
            raise Exception(f"HeyGen video generation failed: {e}")
    
    async def _poll_heygen_status(self, session: aiohttp.ClientSession, headers: Dict, video_id: str) -> Optional[str]:
        """Poll HeyGen API for video completion status using /video_status/{video_id} endpoint"""
        max_attempts = 120  # 10 minutes with 5-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Use the video_status endpoint to check completion and get video URL
                async with session.get(
                    f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        data = result.get('data', {})
                        status = data.get('status')
                        
                        logger.info(f"HeyGen status check {attempt + 1}: {status}")
                        
                        if status == 'completed':
                            # Look for video URL in multiple possible locations
                            video_url = None
                            
                            # Try different possible field names for video URL
                            possible_fields = ['video_url', 'url', 'download_url', 'file_url', 'video']
                            for field in possible_fields:
                                if field in data and data[field]:
                                    video_url = data[field]
                                    break
                            
                            # Also check if there's a nested structure
                            if not video_url and 'video' in data and isinstance(data['video'], dict):
                                for field in possible_fields:
                                    if field in data['video'] and data['video'][field]:
                                        video_url = data['video'][field]
                                        break
                            
                            logger.info(f"Full HeyGen response data: {data}")
                            
                            if video_url and isinstance(video_url, str) and video_url.startswith('http'):
                                logger.info(f"HeyGen video completed: {video_url}")
                                return video_url
                            else:
                                logger.warning(f"Video completed but no valid URL found in response. Available fields: {list(data.keys())}")
                                logger.warning(f"Full response: {data}")
                        elif status == 'failed':
                            logger.error(f"HeyGen video generation failed: {data}")
                            raise Exception(f"HeyGen video generation failed: {data.get('error', 'Unknown error')}")
                        else:
                            logger.info(f"HeyGen video still processing, status: {status}")
                    else:
                        response_text = await response.text()
                        logger.warning(f"HeyGen status API response {response.status}: {response_text}")
                
                await asyncio.sleep(5)
                attempt += 1
                
            except Exception as e:
                logger.error(f"Error polling HeyGen status: {e}")
                await asyncio.sleep(5)
                attempt += 1
        
        logger.error("HeyGen video generation timed out")
        raise Exception("HeyGen video generation timed out after 10 minutes")
    
    async def _download_video(self, session: aiohttp.ClientSession, video_url: str, game_title: str, module_type: str) -> Optional[str]:
        """Download video from URL, save locally, and upload to Cloudinary"""
        try:
            # Clean filename
            safe_title = "".join(c for c in game_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_{module_type}.mp4"
            
            # Ensure directory exists
            save_dir = self.config.ASSETS_PATH / f"{module_type}s"
            save_dir.mkdir(parents=True, exist_ok=True)
            file_path = save_dir / filename
            
            # Check if this is a HeyGen share URL that needs to be converted to direct video URL
            if "app.heygen.com/share/" in video_url:
                logger.info(f"Converting HeyGen share URL to direct video URL: {video_url}")
                # Extract the share ID and construct the direct video URL
                share_id = video_url.split("/share/")[-1]
                # Try different possible direct video URL formats
                direct_urls = [
                    f"https://resource.heygen.com/video/{share_id}.mp4",
                    f"https://app.heygen.com/videos/{share_id}.mp4",
                    f"https://cdn.heygen.com/{share_id}.mp4"
                ]
                
                # Try each possible direct URL
                for direct_url in direct_urls:
                    try:
                        async with session.get(direct_url) as response:
                            if response.status == 200 and 'video' in response.headers.get('content-type', ''):
                                content = await response.read()
                                with open(file_path, 'wb') as f:
                                    f.write(content)
                                logger.info(f"Downloaded {module_type} video from {direct_url}: {file_path}")
                                
                                # Upload to Cloudinary and return URL
                                cloudinary_url = await self._upload_to_cloudinary(str(file_path), f"{module_type}_{game_title}")
                                return cloudinary_url
                    except Exception as e:
                        logger.warning(f"Failed to download from {direct_url}: {e}")
                        continue
                
                # If direct URLs don't work, try the original share URL
                logger.warning("Direct URLs failed, trying original share URL")
            
            # Download from the original URL
            async with session.get(video_url) as response:
                if response.status == 200:
                    content = await response.read()
                    content_type = response.headers.get('content-type', '')
                    logger.info(f"Downloaded content type: {content_type}, size: {len(content)} bytes")
                    
                    # Check if it's actually video content
                    if 'video' not in content_type and len(content) < 1000000:  # Less than 1MB might be HTML
                        logger.error(f"Downloaded content doesn't appear to be a video. Content-Type: {content_type}")
                        # Try to extract actual video URL from HTML if it's a web page
                        content_str = content.decode('utf-8', errors='ignore')
                        if 'video' in content_str.lower():
                            logger.info("Content appears to be HTML, might contain video URL")
                        return None
                    
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    logger.info(f"Downloaded {module_type} video: {file_path}")
                    
                    # Upload to Cloudinary and return URL
                    cloudinary_url = await self._upload_to_cloudinary(str(file_path), f"{module_type}_{game_title}")
                    return cloudinary_url
                else:
                    logger.error(f"Failed to download video: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            raise Exception(f"Video download failed: {e}")
    
    async def download_heygen_and_upload_cloudinary(self, video_id: str, game_title: str) -> str:
        """Download HeyGen video using official API and upload to Cloudinary with public access"""
        # Create SSL context that doesn't verify certificates (for development)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            headers = {
                'X-API-Key': Config.HEYGEN_API_KEY,
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Using HeyGen official API to download video ID: {video_id}")
            
            # First try "Retrieve Video Status/Details" endpoint to get video details
            async with session.get(
                f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"HeyGen download API response: {result}")
                    
                    # Look for video URL in various possible fields
                    data = result.get('data', {})
                    download_url = None
                    
                    # Try different possible field names for the video URL in status response
                    possible_fields = ['video_url', 'download_url', 'url', 'video', 'file_url', 'mp4_url', 'video_file', 'output_url']
                    for field in possible_fields:
                        if isinstance(data, dict) and field in data:
                            url = data[field]
                            if url and isinstance(url, str) and url.startswith('http'):
                                download_url = url
                                logger.info(f"Found video URL in field '{field}': {url}")
                                break
                    
                    # If data is directly a URL string
                    if not download_url and isinstance(data, str) and data.startswith('http'):
                        download_url = data
                        logger.info(f"Found video URL directly in data: {data}")
                    
                    if download_url:
                        logger.info(f"Got official download URL: {download_url}")
                        
                        # Download the video using the official URL
                        async with session.get(download_url) as vid_response:
                            if vid_response.status == 200:
                                video_content = await vid_response.read()
                                content_type = vid_response.headers.get('content-type', '')
                                logger.info(f"Downloaded video: {len(video_content)} bytes, content-type: {content_type}")
                                
                                # Save video locally
                                safe_title = "".join(c for c in game_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                                filename = f"{safe_title}_intro.mp4"
                                save_dir = self.config.ASSETS_PATH / "intros"
                                save_dir.mkdir(parents=True, exist_ok=True)
                                file_path = save_dir / filename
                                
                                with open(file_path, 'wb') as f:
                                    f.write(video_content)
                                
                                logger.info(f"Saved video to: {file_path}")
                                
                                # Upload to Cloudinary with public access
                                cloudinary_url = await self._upload_to_cloudinary_public(str(file_path), f"intro_{game_title}")
                                logger.info(f"✅ Successfully processed HeyGen video: {cloudinary_url}")
                                return cloudinary_url
                            else:
                                logger.error(f"Failed to download from official URL: {vid_response.status}")
                                raise Exception(f"Failed to download video from official URL: {vid_response.status}")
                    else:
                        logger.error(f"Invalid download URL in response: {result}")
                        raise Exception(f"HeyGen API returned invalid download URL: {result}")
                else:
                    error_text = await response.text()
                    logger.error(f"HeyGen video_status API failed: {response.status} - {error_text}")
                    raise Exception(f"HeyGen video_status API failed with status {response.status}: {error_text}")
                    
        raise Exception("Failed to download HeyGen video using official API")
    
    async def _upload_to_cloudinary_public(self, file_path: str, public_id: str) -> str:
        """Upload video to Cloudinary with maximum public accessibility"""
        try:
            logger.info(f"Uploading to Cloudinary with public access: {file_path}")
            
            # Clean public_id to avoid URL encoding issues
            clean_public_id = public_id.replace(" ", "_").replace(":", "").replace("'", "").replace("%", "")
            
            # Upload video to Cloudinary with maximum public accessibility
            result = cloudinary.uploader.upload(
                file_path,
                resource_type="video",
                public_id=clean_public_id,
                folder="youtube_reels",
                overwrite=True,
                type="upload",
                access_mode="public",
                use_filename=False,
                unique_filename=True,
                # Maximum public accessibility settings
                secure=False,  # Use HTTP instead of HTTPS
                invalidate=True,  # Clear CDN cache
                format="mp4",  # Ensure MP4 format
                # Additional settings for public access
                transformation=[
                    {"quality": "auto"},
                    {"format": "mp4"}
                ]
            )
            
            # Use HTTP URL for better compatibility
            cloudinary_url = result.get('url', result.get('secure_url'))
            if cloudinary_url and cloudinary_url.startswith('https://'):
                cloudinary_url = cloudinary_url.replace('https://', 'http://')
            
            logger.info(f"✅ Uploaded to Cloudinary with public access: {cloudinary_url}")
            return cloudinary_url
            
        except Exception as e:
            logger.error(f"Error uploading to Cloudinary: {e}")
            raise Exception(f"Cloudinary upload failed: {e}")
    
    async def _upload_to_cloudinary(self, file_path: str, public_id: str) -> str:
        try:
            logger.info(f"Uploading to Cloudinary: {file_path}")
            
            # Clean public_id to avoid URL encoding issues
            clean_public_id = public_id.replace(" ", "_").replace(":", "").replace("'", "").replace("%", "")
            
            # Upload video to Cloudinary with maximum public accessibility
            result = cloudinary.uploader.upload(
                file_path,
                resource_type="video",
                public_id=clean_public_id,
                folder="youtube_reels",
                overwrite=True,
                type="upload",
                access_mode="public",
                use_filename=False,
                unique_filename=True,
                # Add additional settings for maximum accessibility
                secure=False,  # Use HTTP instead of HTTPS for better compatibility
                invalidate=True,  # Clear CDN cache
                format="mp4"  # Ensure MP4 format
            )
            
            # Use the regular URL instead of secure_url for better Creatomate compatibility
            cloudinary_url = result.get('url', result['secure_url'])
            logger.info(f"✅ Uploaded to Cloudinary: {cloudinary_url}")
            return cloudinary_url
            
        except Exception as e:
            logger.error(f"Error uploading to Cloudinary: {e}")
            raise Exception(f"Cloudinary upload failed: {e}")
    
    def download_heygen_video(self, heygen_url: str) -> str:
        """Download HeyGen video to temporary file - handles share URLs by finding direct video URLs"""
        try:
            logger.info(f"Downloading HeyGen video from: {heygen_url}")
            
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.mp4')
            os.close(temp_fd)  # Close file descriptor, we'll use the path
            
            # Check if this is a HeyGen share URL that needs conversion
            if "/share/" in heygen_url:
                logger.info("Converting HeyGen share URL to direct video URL")
                share_id = heygen_url.split("/share/")[-1]
                logger.info(f"Extracted share ID: {share_id}")
                
                # Try different possible direct video URLs (same logic as existing method)
                possible_urls = [
                    f"https://app.heygen.com/videos/{share_id}.mp4",
                    f"https://resource.heygen.com/{share_id}.mp4", 
                    f"https://cdn.heygen.com/video/{share_id}.mp4",
                    f"https://heygen-public.s3.amazonaws.com/{share_id}.mp4"
                ]
                
                video_found = False
                for video_url in possible_urls:
                    try:
                        logger.info(f"Trying video URL: {video_url}")
                        response = requests.get(video_url, stream=True)
                        
                        if response.status_code == 200:
                            content_type = response.headers.get('content-type', '')
                            if 'video' in content_type:
                                logger.info(f"Found video at: {video_url}")
                                
                                with open(temp_path, 'wb') as f:
                                    total_size = 0
                                    for chunk in response.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                        total_size += len(chunk)
                                
                                logger.info(f"Downloaded HeyGen video to: {temp_path} ({total_size} bytes)")
                                video_found = True
                                break
                                
                    except Exception as e:
                        logger.warning(f"Failed to download from {video_url}: {e}")
                        continue
                
                if not video_found:
                    raise Exception(f"Could not find downloadable video at any of the attempted URLs for share ID: {share_id}")
                    
            else:
                # Direct URL - download normally
                response = requests.get(heygen_url, stream=True)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', 'unknown')
                logger.info(f"Response content-type: {content_type}, content-length: {content_length}")
                
                with open(temp_path, 'wb') as f:
                    total_size = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        total_size += len(chunk)
                
                logger.info(f"Downloaded HeyGen video to: {temp_path} ({total_size} bytes)")
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error downloading HeyGen video: {e}")
            raise Exception(f"HeyGen video download failed: {e}")
    
    def upload_heygen_to_cloudinary(self, temp_path: str, key: str) -> str:
        """Upload HeyGen video from temp file to Cloudinary with maximum public access"""
        try:
            logger.info(f"Uploading HeyGen video to Cloudinary: {key}")
            
            # Clean public_id to avoid URL encoding issues
            clean_public_id = key.replace(" ", "_").replace(":", "").replace("'", "").replace("%", "")
            
            # Upload video to Cloudinary with maximum public accessibility
            result = cloudinary.uploader.upload(
                temp_path,
                resource_type="video",
                public_id=f"heygen_{clean_public_id}",
                folder="youtube_reels/heygen",
                overwrite=True,
                type="upload",
                access_mode="public",
                use_filename=False,
                unique_filename=True,
                # Maximum public accessibility settings
                secure=False,  # Use HTTP instead of HTTPS
                invalidate=True,  # Clear CDN cache
                format="mp4",  # Ensure MP4 format
                # Additional settings for public access
                transformation=[
                    {"quality": "auto:good"},
                    {"format": "mp4"}
                ]
            )
            
            # Use HTTP URL for better Creatomate compatibility
            cloudinary_url = result.get('url', result.get('secure_url'))
            if cloudinary_url and cloudinary_url.startswith('https://'):
                cloudinary_url = cloudinary_url.replace('https://', 'http://')
            
            logger.info(f"✅ Uploaded HeyGen video to Cloudinary: {cloudinary_url}")
            return cloudinary_url
            
        except Exception as e:
            logger.error(f"Error uploading HeyGen video to Cloudinary: {e}")
            raise Exception(f"Cloudinary upload failed: {e}")
    
    def process_heygen_for_creatomate(self, heygen_video_urls: dict) -> dict:
        """Complete HeyGen to Cloudinary processing for Creatomate compatibility"""
        logger.info(f"Processing {len(heygen_video_urls)} HeyGen videos for Creatomate")
        cloudinary_urls = {}
        
        for key, heygen_url in heygen_video_urls.items():
            try:
                logger.info(f"Processing HeyGen video: {key}")
                
                # Download from HeyGen
                temp_path = self.download_heygen_video(heygen_url)
                
                # Upload to Cloudinary with public access
                cloudinary_url = self.upload_heygen_to_cloudinary(temp_path, key)
                cloudinary_urls[key] = cloudinary_url
                
                # Cleanup temporary file
                os.unlink(temp_path)
                logger.info(f"✅ Successfully processed {key}: {cloudinary_url}")
                
            except Exception as e:
                logger.error(f"Failed to process HeyGen video {key}: {e}")
                # Clean up temp file if it exists
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise Exception(f"Failed to process HeyGen video {key}: {e}")
        
        logger.info(f"✅ Successfully processed all {len(cloudinary_urls)} HeyGen videos for Creatomate")
        return cloudinary_urls

    def test_process_heygen_for_creatomate(self) -> dict:
        """Test the process_heygen_for_creatomate function with sample URLs"""
        logger.info("🧪 Testing process_heygen_for_creatomate function")
        
        # Sample HeyGen URLs for testing (these should be real URLs from your HeyGen dashboard)
        test_heygen_urls = {
            "intro": "https://app.heygen.com/share/ed0cd544c65d49bf88a0a1659f53fc55",
            "outro": "https://app.heygen.com/share/ed0cd544c65d49bf88a0a1659f53fc55"  # Using same URL for test
        }
        
        try:
            # Process the URLs
            cloudinary_urls = self.process_heygen_for_creatomate(test_heygen_urls)
            
            logger.info("✅ Test completed successfully!")
            logger.info(f"Results: {cloudinary_urls}")
            return cloudinary_urls
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise e

    async def create_intro(self, game_title: str, game_details: Dict = None) -> Optional[str]:
        """Main method to create intro video"""
        try:
            logger.info(f"Creating intro for {game_title}")
            
            # Generate script
            script = await self.generate_intro_script(game_title, game_details)
            
            # Generate video with HeyGen
            video_path = await self.generate_heygen_video(script, game_title)
            
            logger.info(f"Intro created successfully: {video_path}")
            return video_path
                
        except Exception as e:
            logger.error(f"Error creating intro: {e}")
            raise Exception(f"Intro creation failed: {e}")
