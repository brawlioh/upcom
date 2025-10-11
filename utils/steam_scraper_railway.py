"""
Railway-compatible Steam scraper without Selenium dependencies
Uses requests and BeautifulSoup only for Railway deployment
"""
import requests
from bs4 import BeautifulSoup
from loguru import logger
import time
import re
from typing import Dict, List, Optional
import json

class SteamScraper:
    def __init__(self):
        """Initialize the scraper with requests session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info("Steam scraper initialized (Railway mode - no Selenium)")

    def get_upcoming_games(self, limit: int = 20) -> List[Dict[str, str]]:
        """Get upcoming games using requests only"""
        try:
            logger.info(f"Fetching {limit} upcoming games using requests...")
            
            # Use Steam API for upcoming games
            url = "https://store.steampowered.com/api/featuredcategories"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                games = []
                
                # Extract games from different categories
                categories = ['coming_soon', 'new_releases', 'top_sellers']
                for category in categories:
                    if category in data and 'items' in data[category]:
                        for item in data[category]['items'][:limit]:
                            game = {
                                'title': item.get('name', 'Unknown Game'),
                                'url': f"https://store.steampowered.com/app/{item.get('id', '')}",
                                'release_date': 'TBA',
                                'image_url': item.get('header_image', ''),
                                'source': 'steam_api',
                                'app_id': str(item.get('id', ''))
                            }
                            games.append(game)
                            if len(games) >= limit:
                                break
                    if len(games) >= limit:
                        break
                
                logger.info(f"✅ Found {len(games)} games via Steam API")
                return games[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching upcoming games: {e}")
        
        # Fallback to hardcoded list
        return self.get_fallback_games(limit)

    def get_game_details(self, app_id: str) -> Dict[str, str]:
        """Get game details using Steam API"""
        try:
            logger.info(f"Fetching details for app_id: {app_id}")
            
            url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if app_id in data and data[app_id]['success']:
                    game_data = data[app_id]['data']
                    
                    details = {
                        'title': game_data.get('name', 'Unknown Game'),
                        'description': game_data.get('short_description', ''),
                        'release_date': game_data.get('release_date', {}).get('date', 'TBA'),
                        'developer': ', '.join(game_data.get('developers', [])),
                        'publisher': ', '.join(game_data.get('publishers', [])),
                        'genres': ', '.join([g['description'] for g in game_data.get('genres', [])]),
                        'tags': ', '.join([c['description'] for c in game_data.get('categories', [])]),
                        'image_url': game_data.get('header_image', ''),
                        'url': f"https://store.steampowered.com/app/{app_id}",
                        'app_id': app_id,
                        'source': 'steam_api'
                    }
                    
                    logger.info(f"✅ Found details for {details['title']}")
                    return details
            
        except Exception as e:
            logger.error(f"Error getting game details: {e}")
        
        return {}

    def search_game_videos(self, game_title: str) -> List[str]:
        """Search for gameplay videos - Railway compatible version"""
        try:
            # This method would need real video search implementation
            # For now, return empty list to avoid placeholder URLs
            logger.info(f"Video search not implemented for Railway deployment: {game_title}")
            return []
            
        except Exception as e:
            logger.error(f"Error searching videos for {game_title}: {e}")
            return []

    def close(self):
        """Close the session"""
        if hasattr(self, 'session'):
            self.session.close()

    def get_fallback_games(self, limit: int = 20) -> List[Dict[str, str]]:
        """Fallback list of popular games when API fails"""
        fallback_games = [
            {
                "title": "Cyberpunk 2077: Phantom Liberty",
                "url": "https://store.steampowered.com/app/2138330/Cyberpunk_2077_Phantom_Liberty/",
                "release_date": "2023",
                "image_url": "",
                "source": "fallback",
                "app_id": "2138330",
                "description": "The highly anticipated expansion to Cyberpunk 2077",
                "tags": ["RPG", "Open World", "Cyberpunk"],
                "developer": "CD PROJEKT RED"
            },
            {
                "title": "The Elder Scrolls VI",
                "url": "https://elderscrolls.bethesda.net/en/tes6",
                "release_date": "TBA",
                "image_url": "",
                "source": "fallback",
                "app_id": "unknown",
                "description": "The next chapter in the Elder Scrolls saga",
                "tags": ["RPG", "Fantasy", "Open World"],
                "developer": "Bethesda Game Studios"
            },
            {
                "title": "Grand Theft Auto VI",
                "url": "https://www.rockstargames.com/",
                "release_date": "TBA",
                "image_url": "",
                "source": "fallback",
                "app_id": "unknown",
                "description": "The next installment in the GTA series",
                "tags": ["Action", "Open World", "Crime"],
                "developer": "Rockstar Games"
            }
        ]
        
        return fallback_games[:limit]
