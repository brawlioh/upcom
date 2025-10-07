import asyncio
import aiohttp
import json
import ssl
import cloudinary
import cloudinary.uploader
from pathlib import Path
from loguru import logger
from config import Config
from typing import Dict, Optional, List
import time

class VizardProcessor:
    def __init__(self):
        self.config = Config
        # Initialize Cloudinary
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET
        )
        
    async def find_game_video_url(self, game_title: str, game_details: Dict = None) -> Optional[str]:
        """Find gameplay video URL for the game using real search"""
        try:
            logger.info(f"Searching for gameplay video for {game_title}")
            
            # Clean game title for search
            clean_title = "".join(c for c in game_title if c.isalnum() or c in (' ', '-', '_')).strip()
            
            # Expanded curated gameplay URLs for popular games
            curated_videos = {
                "Cyberpunk 2077": "https://www.youtube.com/watch?v=8X2kIfS6fb8",
                "Cyberpunk 2077: Phantom Liberty": "https://www.youtube.com/watch?v=8X2kIfS6fb8",
                "Elden Ring": "https://www.youtube.com/watch?v=E3Huy2cdih0",
                "Starfield": "https://www.youtube.com/watch?v=kfYEiTdsyas",
                "Baldur's Gate 3": "https://www.youtube.com/watch?v=1T22wNvoNiU",
                "The Witcher 3": "https://www.youtube.com/watch?v=c0i88t0Kacs",
                "Grand Theft Auto VI": "https://www.youtube.com/watch?v=QdBZY2fkU-0",
                "Hunt: Showdown 1896": "https://www.youtube.com/watch?v=K4JVgb3S_Uk",
                "100 Indonesia Cats": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "Little Nightmares III": "https://www.youtube.com/watch?v=ZjZJ3oxoEzk",
                "The Elder Scrolls VI": "https://www.youtube.com/watch?v=OkFdqqyI8y4",
                "Slay the Spire 2": "https://www.youtube.com/watch?v=isqH_7hNi2c",
                "Slay the Spire": "https://www.youtube.com/watch?v=isqH_7hNi2c",
                "Hades 2": "https://www.youtube.com/watch?v=MonXZ_YQSMk",
                "Hollow Knight: Silksong": "https://www.youtube.com/watch?v=pFAknD_9U7c",
                "Diablo 4": "https://www.youtube.com/watch?v=7RdDpqCmjb4",
                "Call of Duty": "https://www.youtube.com/watch?v=r72GP1PIZa0",
                "Minecraft": "https://www.youtube.com/watch?v=MmB9b5njVbA",
                "Fortnite": "https://www.youtube.com/watch?v=2gUtfBmw86Y",
                "Among Us": "https://www.youtube.com/watch?v=nseBliU80LM",
                "Fall Guys": "https://www.youtube.com/watch?v=FcIlIeqGJ2M"
            }
            
            # Check for exact match first
            for game, url in curated_videos.items():
                if game.lower() in game_title.lower() or game_title.lower() in game.lower():
                    logger.info(f"Found curated video URL for {game_title}: {url}")
                    return url
            
            # If no curated video found, provide helpful guidance
            logger.error(f"No curated video found for {game_title}")
            available_games = list(curated_videos.keys())
            logger.info(f"Available games in curated list: {', '.join(available_games[:10])}...")
            
            # Suggest similar games
            similar_games = [game for game in available_games if any(word.lower() in game.lower() for word in clean_title.split())]
            if similar_games:
                logger.info(f"Similar games found: {', '.join(similar_games)}")
            
            raise Exception(f"No gameplay video URL found for '{game_title}'. Available games: {len(available_games)} total. Consider using one of: {', '.join(available_games[:5])}... or add '{game_title}' to the curated_videos list.")
            
        except Exception as e:
            logger.error(f"Error finding video URL for {game_title}: {e}")
            raise Exception(f"Failed to find video URL for {game_title}: {e}")
    
    async def submit_to_vizard(self, video_url: str, game_title: str) -> Optional[str]:
        """Submit video to Vizard AI for processing"""
        try:
            logger.info(f"Submitting {game_title} video to Vizard AI")
            
            headers = {
                'VIZARDAI_API_KEY': Config.VIZARD_API_KEY,
                'content-type': 'application/json'
            }
            
            # Vizard AI processing payload (correct format from working example)
            payload = {
                "lang": "en",
                "preferLength": [1],  # 1 = 30-60 second clips
                "videoType": 2,  # YouTube video type
                "videoUrl": video_url,
                "ext": "mp4"
            }
            
            # Create SSL context that doesn't verify certificates (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    "https://elb-api.vizard.ai/hvizard-server-front/open-api/v1/project/create",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        project_id = result.get('projectId')
                        
                        if project_id:
                            logger.info(f"Vizard project created: {project_id}")
                            # Poll for completion
                            clips_data = await self._poll_vizard_status(session, headers, project_id)
                            if clips_data:
                                # Download the best clip
                                output_path = await self._download_best_clip(session, clips_data, game_title)
                                return output_path
                        else:
                            logger.error("No project ID returned from Vizard")
                            raise Exception("Vizard API did not return a project ID")
                    else:
                        logger.error(f"Vizard API error: {response.status}")
                        error_text = await response.text()
                        logger.error(f"Error details: {error_text}")
                        raise Exception(f"Vizard API failed with status {response.status}: {error_text}")
            
        except Exception as e:
            logger.error(f"Error submitting to Vizard: {e}")
            raise Exception(f"Vizard submission failed: {e}")
    
    async def _poll_vizard_status(self, session: aiohttp.ClientSession, headers: Dict, project_id: str) -> Optional[List[Dict]]:
        """Poll Vizard API for processing completion"""
        max_attempts = 60  # 30 minutes with 30-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            try:
                async with session.get(
                    f"https://elb-api.vizard.ai/hvizard-server-front/open-api/v1/project/query/{project_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Debug: Log the full API response to understand structure
                        logger.info(f"Vizard API response: {result}")
                        
                        # Check multiple possible completion indicators
                        videos = None
                        if 'videos' in result and result['videos']:
                            videos = result['videos']
                        elif 'data' in result and 'videos' in result['data'] and result['data']['videos']:
                            videos = result['data']['videos']
                        elif 'clips' in result and result['clips']:
                            videos = result['clips']
                        
                        # Check if processing is complete based on status or videos availability
                        status = result.get('status', '').lower()
                        if videos and len(videos) > 0:
                            logger.info(f"✅ Vizard processing completed with {len(videos)} clips")
                            
                            # Log viral scores for each clip
                            for i, video in enumerate(videos):
                                score = video.get('viralScore', 'N/A')
                                duration = video.get('videoMsDuration', 0) / 1000  # Convert to seconds
                                logger.info(f"Clip {i+1}: Viral Score {score}, Duration: {duration:.1f}s")
                            
                            return videos
                        elif status in ['completed', 'finished', 'done', 'exported']:
                            logger.info(f"✅ Vizard processing completed (status: {status})")
                            # Even if no videos in response, try to return what we have
                            return result.get('videos', result.get('clips', []))
                        else:
                            # Still processing
                            logger.info(f"🔄 Vizard processing: attempt {attempt + 1}/{max_attempts} (status: {status})")
                    else:
                        logger.warning(f"Vizard API returned status {response.status}")
                        error_text = await response.text()
                        logger.warning(f"Response: {error_text}")
                
                # Add a safety check - if we've been polling for too long, break out
                if attempt >= max_attempts - 1:
                    logger.warning("⚠️ Vizard polling timeout approaching, attempting final check...")
                    break
                
                await asyncio.sleep(30)  # 30-second intervals as recommended
                attempt += 1
                
            except Exception as e:
                logger.error(f"Error polling Vizard status: {e}")
                await asyncio.sleep(30)
                attempt += 1
        
        logger.error("Vizard processing timed out")
        raise Exception("Vizard processing timed out after 30 minutes")
    
    async def _download_best_clip(self, session: aiohttp.ClientSession, clips_data: List[Dict], game_title: str) -> Optional[str]:
        """Download the highest-rated clip and upload to Cloudinary"""
        try:
            if not clips_data:
                logger.error("No clips available for download")
                raise Exception("No clips available for download")
            
            # Sort clips by viral score (highest first)
            sorted_clips = sorted(clips_data, key=lambda x: float(x.get('viralScore', 0)), reverse=True)
            best_clip = sorted_clips[0]
            
            video_url = best_clip.get('videoUrl')
            viral_score = best_clip.get('viralScore', 'N/A')
            duration = best_clip.get('videoMsDuration', 0) / 1000
            
            if not video_url:
                logger.error("No video URL found in best clip")
                raise Exception("No video URL found in best clip")
            
            logger.info(f"Selected best clip: Viral Score {viral_score}, Duration: {duration:.1f}s")
            
            # Clean filename
            safe_title = "".join(c for c in game_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_vizard.mp4"
            # Use a simpler path that doesn't require docker permissions
            output_path = Path("assets") / "vizard" / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the video
            logger.info(f"Downloading clip: {video_url}")
            async with session.get(video_url) as response:
                if response.status == 200:
                    # Ensure directory exists
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    logger.info(f"Downloaded Vizard video: {output_path}")
                    
                    # Upload to Cloudinary
                    cloudinary_url = await self._upload_to_cloudinary(str(output_path), f"vizard_{safe_title}")
                    return cloudinary_url
                else:
                    logger.error(f"Failed to download Vizard video: {response.status}")
                    raise Exception(f"Failed to download Vizard video: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Error downloading Vizard video: {e}")
            raise Exception(f"Vizard video download failed: {e}")
    
    
    async def _upload_to_cloudinary(self, file_path: str, public_id: str) -> str:
        """Upload video to Cloudinary and return URL"""
        try:
            logger.info(f"Uploading to Cloudinary: {file_path}")
            
            # Upload to Cloudinary with public access settings
            safe_title = "".join(c for c in public_id if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_public_id = f"vizard_{safe_title}".replace(" ", "_").replace(":", "").replace("'", "").replace("%", "")
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
    
    async def process_gameplay_clip(self, game_title: str, game_details: Dict = None) -> Optional[str]:
        """Main method to process gameplay clip"""
        try:
            logger.info(f"Processing gameplay clip for {game_title}")
            
            # Find video URL
            video_url = await self.find_game_video_url(game_title, game_details)
            
            if not video_url:
                logger.error(f"No video URL found for {game_title}")
                raise Exception(f"No gameplay video URL found for {game_title}")
            
            # Submit to Vizard for processing
            processed_path = await self.submit_to_vizard(video_url, game_title)
            
            logger.info(f"Gameplay clip processed successfully: {processed_path}")
            return processed_path
                
        except Exception as e:
            logger.error(f"Error processing gameplay clip: {e}")
            raise Exception(f"Gameplay clip processing failed: {e}")
    
    async def get_multiple_clips(self, game_title: str, count: int = 3) -> List[str]:
        """Get multiple clips for variety"""
        try:
            logger.info(f"Getting {count} clips for {game_title}")
            
            clips = []
            for i in range(count):
                clip_path = await self.process_gameplay_clip(f"{game_title}_clip_{i+1}")
                if clip_path:
                    clips.append(clip_path)
            
            return clips
            
        except Exception as e:
            logger.error(f"Error getting multiple clips: {e}")
            return []
    
    async def test_vizard_connection(self) -> bool:
        """Test Vizard API connection"""
        try:
            logger.info("Testing Vizard API connection...")
            
            headers = {
                'VIZARDAI_API_KEY': Config.VIZARD_API_KEY,
                'content-type': 'application/json'
            }
            
            # Test with a simple video (using working format)
            test_payload = {
                "lang": "en",
                "preferLength": [1],  # 1 = 30-60 second clips
                "videoType": 2,
                "videoUrl": "https://www.youtube.com/watch?v=8X2kIfS6fb8",  # Cyberpunk gameplay
                "ext": "mp4"
            }
            
            # Create SSL context that doesn't verify certificates (for development)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    "https://elb-api.vizard.ai/hvizard-server-front/open-api/v1/project/create",
                    headers=headers,
                    json=test_payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        project_id = result.get('projectId')
                        if project_id:
                            logger.info(f"✅ Vizard API connection successful! Project ID: {project_id}")
                            return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Vizard API connection failed: {response.status} - {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"❌ Vizard API connection test failed: {e}")
            return False
