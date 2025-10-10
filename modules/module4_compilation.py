import asyncio
import aiohttp
import json
from pathlib import Path
from loguru import logger
from config import Config
from typing import Dict, Optional, List
import time

class CreatorMateCompiler:
    def __init__(self):
        self.config = Config
        
    async def create_compilation_template(self, game_title: str) -> Dict:
        """Create Creatomate template for video compilation"""
        template = {
            "width": Config.VIDEO_WIDTH,
            "height": Config.VIDEO_HEIGHT,
            "duration": None,  # Will be calculated based on clips
            "frame_rate": Config.VIDEO_FPS,
            "elements": [
                {
                    "id": "background",
                    "type": "fill",
                    "track": 1,
                    "time": 0,
                    "duration": None,
                    "fill_color": "#000000"
                },
                {
                    "id": "intro_video",
                    "type": "video",
                    "track": 2,
                    "time": 0,
                    "duration": None,
                    "source": None,  # Will be set dynamically
                    "volume": 0.8,
                    "fit": "cover"
                },
                {
                    "id": "transition_1",
                    "type": "fill",
                    "track": 3,
                    "time": None,  # Will be calculated
                    "duration": 0.5,
                    "fill_color": "#ffffff",
                    "opacity": 0.3
                },
                {
                    "id": "vizard_video",
                    "type": "video",
                    "track": 2,
                    "time": None,  # Will be calculated
                    "duration": None,
                    "source": None,  # Will be set dynamically
                    "volume": 0.9,
                    "fit": "cover"
                },
                {
                    "id": "transition_2",
                    "type": "fill",
                    "track": 3,
                    "time": None,  # Will be calculated
                    "duration": 0.5,
                    "fill_color": "#ffffff",
                    "opacity": 0.3
                },
                {
                    "id": "outro_video",
                    "type": "video",
                    "track": 2,
                    "time": None,  # Will be calculated
                    "duration": None,
                    "source": None,  # Will be set dynamically
                    "volume": 0.8,
                    "fit": "cover"
                },
                {
                    "id": "game_title_text",
                    "type": "text",
                    "track": 4,
                    "time": 1,
                    "duration": 3,
                    "text": game_title,
                    "font_family": "Montserrat",
                    "font_weight": "bold",
                    "font_size": 48,
                    "fill_color": "#ffffff",
                    "stroke_color": "#000000",
                    "stroke_width": 2,
                    "x": "50%",
                    "y": "10%",
                    "alignment": "center"
                }
            ]
        }
        return template
    
    async def upload_assets_to_creatomate(self, intro_path: str, vizard_path: str, outro_path: str) -> Dict[str, str]:
        """Upload video assets to Creatomate"""
        try:
            logger.info("Uploading assets to Creatomate")
            
            headers = {
                'Authorization': f'Bearer {Config.CREATOMATE_API_KEY}',
            }
            
            uploaded_urls = {}
            
            # Upload each asset
            for asset_name, asset_path in [("intro", intro_path), ("vizard", vizard_path), ("outro", outro_path)]:
                if asset_path and Path(asset_path).exists():
                    async with aiohttp.ClientSession() as session:
                        with open(asset_path, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('file', f, filename=Path(asset_path).name)
                            
                            async with session.post(
                                f"{Config.CREATOMATE_BASE_URL}/assets",
                                headers=headers,
                                data=data
                            ) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    uploaded_urls[asset_name] = result.get('url')
                                    logger.info(f"Uploaded {asset_name}: {uploaded_urls[asset_name]}")
                                else:
                                    logger.error(f"Failed to upload {asset_name}: {response.status}")
                else:
                    logger.warning(f"Asset not found: {asset_path}")
            
            return uploaded_urls
            
        except Exception as e:
            logger.error(f"Error uploading assets to Creatomate: {e}")
            return {}
    
    async def get_video_duration(self, video_path: str) -> float:
        """Get video duration (placeholder - would use ffprobe in production)"""
        try:
            # In production, you'd use ffprobe or moviepy to get actual duration
            # For now, return estimated durations
            if "intro" in video_path:
                return 15.0  # 15 seconds for intro
            elif "vizard" in video_path:
                return 30.0  # 30 seconds for gameplay
            elif "outro" in video_path:
                return 10.0  # 10 seconds for outro
            else:
                return 10.0  # Default
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return 10.0
    
    async def create_compilation(self, intro_url: str, vizard_url: str, outro_url: str, game_title: str) -> Optional[str]:
        """Create final compilation using Creatomate with Cloudinary URLs"""
        try:
            logger.info(f"Creating compilation for {game_title}")
            logger.info(f"Processing URLs for Creatomate compatibility:")
            logger.info(f"  Intro: {intro_url}")
            logger.info(f"  Vizard: {vizard_url}")
            logger.info(f"  Outro: {outro_url}")
            
            # For now, use URLs directly and let Creatomate handle them
            # If HeyGen URLs fail, we'll need a different approach
            cloudinary_urls = {
                "intro": intro_url,
                "vizard": vizard_url,
                "outro": outro_url
            }
            
            logger.info(f"Using URLs directly with Creatomate:")
            logger.info(f"  Intro: {cloudinary_urls['intro']}")
            logger.info(f"  Vizard: {cloudinary_urls['vizard']}")
            logger.info(f"  Outro: {cloudinary_urls['outro']}")
            
            logger.info("Using dynamic Creatomate timing references for seamless video flow")
            
            # Note: If Creatomate fails with HeyGen URLs, we may need to:
            # 1. Use a different video compilation service
            # 2. Find a way to get direct download URLs from HeyGen
            # 3. Use a proxy service to convert HeyGen URLs
            
            # Let Creatomate auto-detect durations and sequence videos seamlessly
            # Use "end" timing to make videos play immediately after each other
            
            # Create Creatomate render payload using the correct format
            render_payload = {
                "source": {
                    "output_format": "mp4",
                    "width": 720,
                    "height": 1280,
                    "elements": [
                        {
                            "id": "intro_element",
                            "name": "intro",
                            "type": "video",
                            "track": 1,
                            "time": 0,
                            "fit": "cover",
                            "source": cloudinary_urls.get("intro")
                        },
                        {
                            "id": "vizard_element", 
                            "name": "vizardai",
                            "type": "video",
                            "track": 1,
                            "time": "auto",
                            "fit": "cover",
                            "source": cloudinary_urls.get("vizard")
                        },
                        {
                            "id": "outro_element",
                            "name": "outro", 
                            "type": "video",
                            "track": 1,
                            "time": "auto",
                            "fit": "cover",
                            "source": cloudinary_urls.get("outro")
                        },
                        {
                            "id": "b3f54cad-f420-49dc-9d41-8a7be19000b7",
                            "name": "logo",
                            "type": "image",
                            "track": 3,
                            "time": 0,
                            "source": "https://res.cloudinary.com/dodod8s0v/image/upload/v1759927553/logo_2_xwogmb.png",
                            "animations": [
                                {
                                    "time": 0,
                                    "transition": True,
                                    "type": "fade"
                                },
                                {
                                    "time": "end",
                                    "duration": 3,
                                    "easing": "quadratic-out",
                                    "reversed": True,
                                    "type": "fade"
                                }
                            ]
                        },
                        {
                            "id": "35ef32ce-7fe7-44c2-87de-c94d18f918be",
                            "name": "Image-N62",
                            "type": "image",
                            "track": 1,
                            "time": "auto",
                            "duration": 3,
                            "fit": "cover",
                            "source": "https://res.cloudinary.com/dodod8s0v/image/upload/v1759926961/outro_2_crwy4x.png",
                            "animations": [
                                {
                                    "time": 0,
                                    "duration": 0.5,
                                    "transition": True,
                                    "type": "fade"
                                }
                            ]
                        }
                    ]
                }
            }
            
            # Submit to Creatomate
            headers = {
                'Authorization': f'Bearer {Config.CREATOMATE_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Create SSL context that doesn't verify certificates (for development)
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    f"{Config.CREATOMATE_BASE_URL}/renders",
                    headers=headers,
                    json=render_payload
                ) as response:
                    if response.status in [200, 202]:  # 202 = Accepted (render queued)
                        result = await response.json()
                        # Handle both single render and array response formats
                        if isinstance(result, list) and len(result) > 0:
                            render_id = result[0].get('id')
                        else:
                            render_id = result.get('id')
                        
                        if render_id:
                            logger.info(f"Creatomate render submitted: {render_id}")
                            # Poll for completion
                            final_url = await self._poll_creatomate_status(session, headers, render_id)
                            if final_url:
                                # Download final video
                                output_path = await self._download_final_video(session, final_url, game_title)
                                return output_path
                        else:
                            logger.error("No render ID returned from Creatomate")
                            raise Exception("Creatomate API did not return a render ID")
                    else:
                        logger.error(f"Creatomate API error: {response.status}")
                        error_text = await response.text()
                        logger.error(f"Error details: {error_text}")
                        raise Exception(f"Creatomate API failed with status {response.status}: {error_text}")
            
        except Exception as e:
            logger.error(f"Error creating compilation: {e}")
            raise Exception(f"Compilation creation failed: {e}")
    
    async def _poll_creatomate_status(self, session: aiohttp.ClientSession, headers: Dict, render_id: str) -> Optional[str]:
        """Poll Creatomate API for render completion"""
        max_attempts = 180  # 15 minutes with 5-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            try:
                async with session.get(
                    f"{Config.CREATOMATE_BASE_URL}/renders/{render_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        status = result.get('status')
                        
                        if status == 'succeeded':
                            output_url = result.get('url')
                            logger.info(f"Creatomate render completed: {output_url}")
                            return output_url
                        elif status == 'failed':
                            error_msg = result.get('error', 'Unknown error')
                            logger.error(f"Creatomate render failed: {error_msg}")
                            logger.error(f"Full Creatomate response: {result}")
                            raise Exception(f"Creatomate render failed: {error_msg}")
                        elif status in ['queued', 'rendering']:
                            progress = result.get('progress', 0)
                            logger.info(f"Creatomate rendering: {progress}%")
                        else:
                            logger.info(f"Creatomate status: {status}")
                
                await asyncio.sleep(5)
                attempt += 1
                
            except Exception as e:
                logger.error(f"Error polling Creatomate status: {e}")
                await asyncio.sleep(5)
                attempt += 1
        
        logger.error("Creatomate render timed out")
        raise Exception("Creatomate render timed out after 15 minutes")
    
    async def _download_final_video(self, session: aiohttp.ClientSession, video_url: str, game_title: str) -> Optional[str]:
        """Download final compiled video"""
        try:
            # Clean filename
            safe_title = "".join(c for c in game_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_final_reel.mp4"
            output_path = Config.OUTPUTS_PATH / "final_reels" / filename
            
            async with session.get(video_url) as response:
                if response.status == 200:
                    with open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    logger.info(f"Downloaded final reel: {output_path}")
                    return str(output_path)
                else:
                    logger.error(f"Failed to download final video: {response.status}")
                    raise Exception(f"Failed to download final video: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Error downloading final video: {e}")
            raise Exception(f"Final video download failed: {e}")
    
    async def compile_reel(self, intro_url: str, vizard_url: str, outro_url: str, game_title: str) -> Optional[str]:
        """Main method to compile final reel using Cloudinary URLs"""
        try:
            logger.info(f"Compiling reel for {game_title}")
            
            # Create compilation using Creatomate with Cloudinary URLs
            final_path = await self.create_compilation(intro_url, vizard_url, outro_url, game_title)
            
            logger.info(f"Reel compiled successfully: {final_path}")
            return final_path
                
        except Exception as e:
            logger.error(f"Error compiling reel: {e}")
            raise Exception(f"Reel compilation failed: {e}")
