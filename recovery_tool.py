#!/usr/bin/env python3
"""
Recovery tool for HeyGen videos that completed but weren't caught by polling
This tool can check for completed videos and download them manually
"""

import asyncio
import aiohttp
import ssl
import sys
from pathlib import Path
from loguru import logger

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from config import Config

async def check_heygen_video_status(video_id: str):
    """Check the status of a specific HeyGen video"""
    try:
        headers = {
            'X-Api-Key': Config.HEYGEN_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Create SSL context that doesn't verify certificates (for development)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    status = result.get('data', {}).get('status')
                    video_url = result.get('data', {}).get('video_url')
                    
                    logger.info(f"Video ID: {video_id}")
                    logger.info(f"Status: {status}")
                    
                    if status == 'completed' and video_url:
                        logger.info(f"✅ Video completed successfully!")
                        logger.info(f"📹 Video URL: {video_url}")
                        return video_url
                    elif status == 'failed':
                        error_msg = result.get('data', {}).get('error', 'Unknown error')
                        logger.error(f"❌ Video generation failed: {error_msg}")
                        return None
                    else:
                        logger.info(f"⏳ Video status: {status}")
                        return None
                else:
                    logger.error(f"❌ API error: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"❌ Error checking video status: {e}")
        return None

async def download_video_from_url(video_url: str, game_title: str, module_type: str):
    """Download video from HeyGen URL"""
    try:
        # Clean filename
        safe_title = "".join(c for c in game_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}_{module_type}.mp4"
        output_path = Config.ASSETS_PATH / f"{module_type}s" / filename
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                if response.status == 200:
                    with open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    logger.info(f"✅ Downloaded video: {output_path}")
                    return str(output_path)
                else:
                    logger.error(f"❌ Failed to download video: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"❌ Error downloading video: {e}")
        return None

async def main():
    """Main recovery function"""
    if len(sys.argv) < 2:
        print("Usage: python3 recovery_tool.py <video_id> [game_title] [module_type]")
        print("Example: python3 recovery_tool.py abc123def456 'Cyberpunk 2077' intro")
        return
    
    video_id = sys.argv[1]
    game_title = sys.argv[2] if len(sys.argv) > 2 else "Unknown Game"
    module_type = sys.argv[3] if len(sys.argv) > 3 else "video"
    
    logger.info(f"🔍 Checking HeyGen video: {video_id}")
    
    # Check video status
    video_url = await check_heygen_video_status(video_id)
    
    if video_url:
        logger.info(f"📥 Downloading video for {game_title}...")
        downloaded_path = await download_video_from_url(video_url, game_title, module_type)
        
        if downloaded_path:
            logger.info(f"🎉 Recovery successful!")
            logger.info(f"📁 Video saved to: {downloaded_path}")
        else:
            logger.error(f"💥 Download failed")
    else:
        logger.error(f"💥 Video not ready or failed")

if __name__ == "__main__":
    asyncio.run(main())
