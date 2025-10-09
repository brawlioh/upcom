#!/usr/bin/env python3
"""
Steam API Scraper - Fetches real game data from Steam using App ID
Gets game title, release date, videos, and other details dynamically
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import json
import re
import ssl

logger = logging.getLogger(__name__)

class SteamAPIScraper:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        # Create SSL context that doesn't verify certificates (for development)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_game_details(self, app_id: str) -> Dict:
        """Get complete game details from Steam App ID"""
        try:
            logger.info(f"🔍 Fetching game details for Steam App ID: {app_id}")
            
            # Method 1: Try Steam Store API first
            steam_data = await self._get_steam_store_data(app_id)
            if steam_data:
                return steam_data
            
            # Method 2: Fallback to SteamDB scraping
            steamdb_data = await self._get_steamdb_data(app_id)
            if steamdb_data:
                return steamdb_data
            
            # Method 3: Fallback to Steam store page scraping
            store_data = await self._get_steam_store_page_data(app_id)
            if store_data:
                return store_data
            
            # If all methods fail, return basic data
            logger.warning(f"⚠️ Could not fetch complete data for App ID {app_id}")
            return {
                "app_id": app_id,
                "name": f"Steam_Game_{app_id}",
                "release_date": "Unknown",
                "developer": "Unknown",
                "publisher": "Unknown",
                "videos": [],
                "description": f"Game with Steam App ID {app_id}"
            }
            
        except Exception as e:
            logger.error(f"Error fetching game details for {app_id}: {e}")
            return {
                "app_id": app_id,
                "name": f"Steam_Game_{app_id}",
                "release_date": "Unknown",
                "developer": "Unknown",
                "publisher": "Unknown", 
                "videos": [],
                "description": f"Game with Steam App ID {app_id}"
            }

    async def _get_steam_store_data(self, app_id: str) -> Optional[Dict]:
        """Get data from Steam Store API"""
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=english"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if app_id in data and data[app_id].get('success'):
                        game_data = data[app_id]['data']
                        
                        # Extract videos
                        videos = []
                        if 'movies' in game_data:
                            for movie in game_data['movies']:
                                if 'mp4' in movie and '480' in movie['mp4']:
                                    videos.append(movie['mp4']['480'])
                        
                        # Extract release date
                        release_date = "Unknown"
                        if 'release_date' in game_data:
                            release_date = game_data['release_date'].get('date', 'Unknown')
                        
                        result = {
                            "app_id": app_id,
                            "name": game_data.get('name', f'Steam_Game_{app_id}'),
                            "release_date": release_date,
                            "developer": ', '.join(game_data.get('developers', ['Unknown'])),
                            "publisher": ', '.join(game_data.get('publishers', ['Unknown'])),
                            "videos": videos,
                            "description": game_data.get('short_description', ''),
                            "genres": [genre['description'] for genre in game_data.get('genres', [])],
                            "tags": [tag for tag in game_data.get('categories', [])]
                        }
                        
                        logger.info(f"✅ Steam Store API: Found '{result['name']}'")
                        return result
                        
        except Exception as e:
            logger.error(f"Steam Store API error: {e}")
            return None

    async def _get_steamdb_data(self, app_id: str) -> Optional[Dict]:
        """Scrape data from SteamDB"""
        try:
            url = f"https://steamdb.info/app/{app_id}/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract game name
                    name_element = soup.find('h1')
                    name = name_element.text.strip() if name_element else f'Steam_Game_{app_id}'
                    
                    # Extract details from the info table
                    details = {}
                    info_rows = soup.find_all('tr')
                    for row in info_rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            key = cells[0].text.strip()
                            value = cells[1].text.strip()
                            details[key] = value
                    
                    result = {
                        "app_id": app_id,
                        "name": name,
                        "release_date": details.get('Release Date', 'Unknown'),
                        "developer": details.get('Developer', 'Unknown'),
                        "publisher": details.get('Publisher', 'Unknown'),
                        "videos": [],  # SteamDB doesn't have direct video links
                        "description": f"Game information from SteamDB for {name}",
                        "last_update": details.get('Last Record Update', 'Unknown')
                    }
                    
                    logger.info(f"✅ SteamDB: Found '{result['name']}'")
                    return result
                    
        except Exception as e:
            logger.error(f"SteamDB scraping error: {e}")
            return None

    async def _get_steam_store_page_data(self, app_id: str) -> Optional[Dict]:
        """Scrape data from Steam store page"""
        try:
            url = f"https://store.steampowered.com/app/{app_id}/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract game name
                    name_element = soup.find('div', class_='apphub_AppName')
                    if not name_element:
                        name_element = soup.find('h1')
                    name = name_element.text.strip() if name_element else f'Steam_Game_{app_id}'
                    
                    # Extract videos
                    videos = []
                    video_elements = soup.find_all('video')
                    for video in video_elements:
                        src = video.get('src')
                        if src:
                            videos.append(src)
                    
                    # Look for YouTube videos in the page
                    youtube_links = soup.find_all('a', href=re.compile(r'youtube\.com|youtu\.be'))
                    for link in youtube_links:
                        href = link.get('href', '')
                        if 'watch?v=' in href or 'youtu.be/' in href:
                            videos.append(href)
                    
                    result = {
                        "app_id": app_id,
                        "name": name,
                        "release_date": "Unknown",
                        "developer": "Unknown",
                        "publisher": "Unknown",
                        "videos": videos[:5],  # Limit to 5 videos
                        "description": f"Game information from Steam store for {name}"
                    }
                    
                    logger.info(f"✅ Steam Store Page: Found '{result['name']}'")
                    return result
                    
        except Exception as e:
            logger.error(f"Steam store page scraping error: {e}")
            return None

    async def get_game_videos(self, app_id: str) -> List[str]:
        """Get video URLs for a specific game"""
        try:
            game_data = await self.get_game_details(app_id)
            videos = game_data.get('videos', [])
            
            if videos:
                logger.info(f"🎬 Found {len(videos)} videos for {game_data['name']}")
                return videos
            else:
                logger.warning(f"⚠️ No videos found for App ID {app_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting videos for {app_id}: {e}")
            return []

# Standalone function for easy import
async def get_steam_game_details(app_id: str) -> Dict:
    """Get Steam game details by App ID"""
    async with SteamAPIScraper() as scraper:
        return await scraper.get_game_details(app_id)

async def get_steam_game_videos(app_id: str) -> List[str]:
    """Get Steam game videos by App ID"""
    async with SteamAPIScraper() as scraper:
        return await scraper.get_game_videos(app_id)
