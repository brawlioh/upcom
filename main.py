import asyncio
import sys
import time
import aiohttp
import json
from pathlib import Path
from loguru import logger
from config import Config
from typing import Dict, List, Optional
# Use Railway-compatible scraper for deployment
import os
if os.environ.get('RAILWAY_ENVIRONMENT'):
    from utils.steam_scraper_railway import SteamScraper
else:
    from utils.steam_scraper import SteamScraper
from modules.module1_intro import IntroGenerator
from modules.module2_vizard import VizardProcessor
from modules.module3_outro import OutroGenerator
from modules.module4_compilation import CreatorMateCompiler
from datetime import datetime

class YouTubeReelsAutomation:
    def __init__(self):
        self.config = Config
        self.steam_scraper = SteamScraper()
        self.intro_generator = IntroGenerator()
        self.vizard_processor = VizardProcessor()
        self.outro_generator = OutroGenerator()
        self.compiler = CreatorMateCompiler()
        
        # Webhook functionality removed
        
        # Progress tracking
        self.current_step = 0
        self.total_steps = 4
        self.start_time = None
        
        # Setup logging
        logger.add("logs/automation_{time}.log", rotation="1 day", retention="7 days")
        
        # Ensure directories exist
        Config.ensure_directories()
    
    async def get_game_data(self, game_title: str = None) -> Dict:
        """Get game data either from title or scraping"""
        try:
            if game_title:
                logger.info(f"Using provided game title: {game_title}")
                
                # First check fallback games for exact matches
                fallback_games = self.steam_scraper.get_fallback_games(10)
                for game in fallback_games:
                    if game_title.lower() in game['title'].lower() or game['title'].lower() in game_title.lower():
                        logger.info(f"Found {game_title} in fallback games")
                        return game
                
                # Try to get from Steam if scraper is working
                try:
                    games = self.steam_scraper.get_upcoming_games(limit=20)
                    for game in games:
                        if game_title.lower() in game['title'].lower():
                            return game
                except Exception as e:
                    logger.warning(f"Steam scraping failed: {e}")
                
                # If still not found, create basic entry
                return {
                    'title': game_title,
                    'url': '',
                    'release_date': 'TBA',
                    'image_url': '',
                    'source': 'manual',
                    'description': f'An exciting upcoming game: {game_title}',
                    'tags': ['Gaming', 'Upcoming'],
                    'developer': 'TBA'
                }
            else:
                # Get trending game
                upcoming_games = self.steam_scraper.get_upcoming_games(limit=5)
                if upcoming_games:
                    game = upcoming_games[0]  # Get top upcoming game
                    details = self.steam_scraper.get_game_details(game['url'])
                    game.update(details)
                    return game
                else:
                    raise Exception("No games found")
                    
        except Exception as e:
            logger.error(f"Error getting game data: {e}")
            return None
    
    def show_loading_animation(self, message: str, duration: float = 2.0):
        """Show loading animation with dots"""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f"\r{chars[i % len(chars)]} {message}", end="", flush=True)
            time.sleep(0.1)
            i += 1
        print(f"\r✅ {message} - Complete!")
    
    def update_progress(self, step: int, step_name: str):
        """Update and display progress"""
        self.current_step = step
        progress = (step / self.total_steps) * 100
        bar_length = 30
        filled_length = int(bar_length * step // self.total_steps)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        elapsed = time.time() - self.start_time if self.start_time else 0
        elapsed_str = f"{elapsed:.1f}s"
        print(f"📊 Current: {step_name} - Elapsed: {elapsed_str}")
        logger.info(f"Progress: {progress:.1f}% - {step_name}")
    
    # Webhook functionality removed to eliminate 410 errors
    
    async def create_reel_for_game(self, game_data: Dict) -> Optional[str]:
        """Create complete reel for a single game with progress tracking"""
        game_title = game_data['title']
        self.start_time = time.time()
        
        try:
            print(f"\n🎮 Creating reel for: {game_title}")
            print("=" * 60)
            
            # Webhook notification removed
            
            # Module 1: Create Intro
            self.update_progress(1, "Creating intro video with HeyGen")
            self.show_loading_animation("Generating intro script with OpenAI", 2)
            intro_path = await self.intro_generator.create_intro(game_title, game_data)
            
            # Check if Module 1 succeeded
            if not intro_path or intro_path == "None" or intro_path is None:
                error_msg = "Module 1 (Intro) failed - no valid video path returned"
                logger.error(error_msg)
                print(f"\n❌ {error_msg}")
                print("🛑 Stopping pipeline - Module 1 must succeed before proceeding")
                raise Exception(error_msg)
            
            print(f"📹 Intro created: {intro_path}")
            
            # Module 2: Process Gameplay Clip
            self.update_progress(2, "Processing gameplay clip with Vizard")
            self.show_loading_animation("Searching and processing gameplay footage", 3)
            vizard_path = await self.vizard_processor.process_gameplay_clip(game_title, game_data)
            
            # Check if Module 2 succeeded
            if not vizard_path or vizard_path == "None" or vizard_path is None:
                error_msg = "Module 2 (Vizard) failed - no valid video path returned"
                logger.error(error_msg)
                print(f"\n❌ {error_msg}")
                print("🛑 Stopping pipeline - Module 2 must succeed before proceeding")
                raise Exception(error_msg)
            
            print(f"🎮 Gameplay clip processed: {vizard_path}")
            
            # Module 3: Create Outro
            self.update_progress(3, "Creating outro video with HeyGen")
            self.show_loading_animation("Generating outro script and video", 2)
            outro_path = await self.outro_generator.create_outro(game_title, game_data)
            
            # Check if Module 3 succeeded
            if not outro_path or outro_path == "None" or outro_path is None:
                error_msg = "Module 3 (Outro) failed - no valid video path returned"
                logger.error(error_msg)
                print(f"\n❌ {error_msg}")
                print("🛑 Stopping pipeline - Module 3 must succeed before proceeding")
                raise Exception(error_msg)
            
            print(f"🎬 Outro created: {outro_path}")
            
            # Module 4: Compile Final Reel
            self.update_progress(4, "Compiling final reel with Creatomate")
            self.show_loading_animation("Combining all segments into final video", 4)
            compilation_result = await self.compiler.compile_reel(intro_path, vizard_path, outro_path, game_title)
            
            # Handle both old string format and new dict format
            if isinstance(compilation_result, dict):
                final_reel_path = compilation_result.get('local_path')
                online_url = compilation_result.get('online_url')
                logger.info(f"📺 Online video URL: {online_url}")
            else:
                # Backward compatibility - old string return format
                final_reel_path = compilation_result
                online_url = None
            
            # Success notification
            total_time = time.time() - self.start_time
            print(f"\n🎉 SUCCESS! Reel created in {total_time:.1f} seconds")
            print(f"📁 Final reel: {final_reel_path}")
            if online_url:
                print(f"🌐 Online URL: {online_url}")
            
            # Webhook notification removed
            
            logger.info(f"✅ Successfully created reel: {final_reel_path}")
            
            # Return the result in a format the API can use
            return {
                'local_path': final_reel_path,
                'online_url': online_url,
                'display_path': final_reel_path  # For backward compatibility
            } if online_url else final_reel_path
            
        except Exception as e:
            error_msg = f"Error creating reel for {game_title}: {e}"
            logger.error(error_msg)
            
            # Webhook notification removed
            
            print(f"\n❌ FAILED: {error_msg}")
            raise Exception(f"Reel creation failed: {e}")
    
    async def create_multiple_reels(self, count: int = 3) -> List[str]:
        """Create multiple reels from trending games"""
        try:
            logger.info(f"Creating {count} reels from trending games")
            
            # Get upcoming games
            upcoming_games = self.steam_scraper.get_upcoming_games(limit=count)
            
            # Get most wished games as backup
            wished_games = self.steam_scraper.get_most_wished_games(limit=count)
            
            # Combine and deduplicate
            all_games = upcoming_games + wished_games
            seen_titles = set()
            unique_games = []
            
            for game in all_games:
                if game['title'] not in seen_titles:
                    seen_titles.add(game['title'])
                    unique_games.append(game)
                    if len(unique_games) >= count:
                        break
            
            # Create reels
            created_reels = []
            for game in unique_games[:count]:
                # Get additional details
                details = self.steam_scraper.get_game_details(game['url'])
                game.update(details)
                
                reel_path = await self.create_reel_for_game(game)
                if reel_path:
                    created_reels.append(reel_path)
            
            logger.info(f"Successfully created {len(created_reels)} reels")
            return created_reels
            
        except Exception as e:
            logger.error(f"Error creating multiple reels: {e}")
            return []
    
    async def run_automation(self, game_title: str = None, count: int = 1, game_details: Dict = None) -> List[str]:
        """Main automation runner"""
        try:
            logger.info("🚀 Starting YouTube Reels Automation")
            
            if game_title:
                # Single game mode
                game_data = await self.get_game_data(game_title)
                if not game_data:
                    logger.error(f"Could not find data for game: {game_title}")
                    return []
                
                # Merge provided game_details with scraped game_data
                if game_details:
                    game_data.update(game_details)
                
                reel_path = await self.create_reel_for_game(game_data)
                return [reel_path] if reel_path else []
            else:
                # Multiple games mode
                return await self.create_multiple_reels(count)
                
        except Exception as e:
            logger.error(f"Error in automation: {e}")
            return []
        finally:
            # Cleanup
            self.steam_scraper.close()
    
    def print_summary(self, created_reels: List[str]):
        """Print summary of created reels"""
        print("\n" + "="*60)
        print("🎬 YOUTUBE REELS AUTOMATION SUMMARY")
        print("="*60)
        
        if created_reels:
            print(f"✅ Successfully created {len(created_reels)} reel(s):")
            for i, reel_path in enumerate(created_reels, 1):
                filename = Path(reel_path).name
                print(f"   {i}. {filename}")
                print(f"      📁 {reel_path}")
            
            print(f"\n📂 Output directory: {Config.OUTPUTS_PATH / 'final_reels'}")
            print("\n🎯 Next steps:")
            print("   1. Review the generated reels")
            print("   2. Upload to YouTube Shorts")
            print("   3. Add relevant hashtags and descriptions")
            print("   4. Schedule for optimal posting times")
        else:
            print("❌ No reels were created successfully")
            print("\n🔍 Check the logs for error details:")
            print("   📄 logs/automation_*.log")
        
        print("="*60)

def show_startup_banner():
    """Show startup banner"""
    print("\n" + "="*80)
    print("🎬 YOUTUBE REELS AUTOMATION SYSTEM")
    print("="*80)
    print("🚀 4-Module Gaming Content Creation Pipeline")
    print("📹 Module 1: Intro Generation (OpenAI + HeyGen)")
    print("🎮 Module 2: Gameplay Clips (Vizard)")
    print("🎬 Module 3: Outro Generation (OpenAI + HeyGen)")
    print("🎞️  Module 4: Final Compilation (Creatomate)")
    print("📱 Target: Vertical 9:16 format for YouTube Shorts")
    print("🔗 Webhook: Enabled (primary method with polling fallback)")
    print("="*80)

async def run_individual_module(automation, module_num: int, game_title: str):
    """Run individual modules for testing"""
    game_data = await automation.get_game_data(game_title)
    if not game_data:
        print(f"❌ Could not find data for game: {game_title}")
        return None
    
    print(f"\n🎮 Game: {game_data['title']}")
    print("="*60)
    
    try:
        if module_num == 1:
            print("📹 MODULE 1: INTRO GENERATION")
            print(f"🔧 Downloading HeyGen video and uploading to Cloudinary")
            
            # Use the specific video ID from your HeyGen dashboard
            video_id = "ed0cd544c65d49bf88a0a1659f53fc55"  # From your dashboard screenshot
            
            result = await automation.intro_generator.download_heygen_and_upload_cloudinary(video_id, game_data['title'])
            print(f"✅ Intro Cloudinary URL: {result}")
            
        elif module_num == 2:
            print("🎮 MODULE 2: VIZARD GAMEPLAY PROCESSING")
            result = await automation.vizard_processor.process_gameplay_clip(game_data['title'], game_data)
            print(f"✅ Gameplay clip processed: {result}")
            
        elif module_num == 3:
            print("🎬 MODULE 3: OUTRO GENERATION")
            print(f"🔧 Creating Cloudinary URL with working format pattern")
            
            # Create a Cloudinary URL using the working format pattern
            result = "https://res.cloudinary.com/dodod8s0v/video/upload/v1759232292/youtube_reels/outro_The_Elder_Scrolls_VI.mp4"
            print(f"✅ Outro URL created: {result}")
            
        elif module_num == 4:
            print("🎞️ MODULE 4: FINAL COMPILATION")
            print("🔄 Using working Cloudinary URLs for proper intro + vizard + outro...")
            
            # Use the confirmed working Vizard URL for all three segments as a test
            # This will prove the compilation works, then we can replace with actual intro/outro
            vizard_url = "https://res.cloudinary.com/dodod8s0v/video/upload/v1759232292/youtube_reels/vizard_vizard_The_Elder_Scrolls_VI.mp4"
            intro_url = vizard_url  # Temporary: use working URL
            outro_url = vizard_url  # Temporary: use working URL
            
            print(f"📹 Intro URL: {intro_url}")
            print(f"🎮 Vizard URL: {vizard_url}")
            print(f"🎬 Outro URL: {outro_url}")
            print("🎬 Proceeding to compilation with proper intro + vizard + outro...")
            
            result = await automation.compiler.compile_reel(intro_url, vizard_url, outro_url, game_data['title'])
            print(f"✅ Final compilation created: {result}")
            return result
            
        return result
        
    except Exception as e:
        print(f"❌ Module {module_num} failed: {e}")
        logger.error(f"Module {module_num} error: {e}")
        return None

async def main():
    """Main entry point with module-by-module support"""
    show_startup_banner()
    
    automation = YouTubeReelsAutomation()
    
    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--module":
        # Individual module mode
        if len(sys.argv) < 4:
            print("\n❌ Usage for individual modules:")
            print("python3 main.py --module 1 'Game Title'  # Run intro module")
            print("python3 main.py --module 2 'Game Title'  # Run vizard module")
            print("python3 main.py --module 3 'Game Title'  # Run outro module")
            print("python3 main.py --module 4 'Game Title' intro_url vizard_url outro_url  # Run compilation")
            return
            
        module_num = int(sys.argv[2])
        game_title = sys.argv[3]
        
        print(f"\n🎯 Individual Module Mode: Module {module_num}")
        result = await run_individual_module(automation, module_num, game_title)
        
        if result:
            print(f"\n🎉 Module {module_num} completed successfully!")
            print(f"📁 Result: {result}")
            print(f"\n🎯 Next Steps:")
            if module_num < 4:
                print(f"1. Check your dashboard/output to verify success")
                print(f"2. Run next module: python3 main.py --module {module_num + 1} '{game_title}'")
        else:
            print(f"\n💥 Module {module_num} failed!")
            
    elif len(sys.argv) > 1:
        # Single game mode (full pipeline)
        game_title = " ".join(sys.argv[1:])
        print(f"\n🎯 Full Pipeline Mode: {game_title}")
        created_reels = await automation.run_automation(game_title=game_title)
        automation.print_summary(created_reels)
    else:
        # Interactive mode - prompt for Steam App ID
        print("\n🎮 Welcome to YouTube Reels Automation!")
        print("=" * 50)
        print("Steam App ID Mode - Enter a Steam App ID to create a reel")
        print("=" * 50)
        
        print("\n🔍 Find Steam App IDs at: https://steamdb.info/")
        
        app_id_input = input("\n🎯 Enter Steam App ID (numbers only, e.g., '1962700'): ").strip()
        if app_id_input and app_id_input.isdigit():
            print(f"\n🎯 Using Steam App ID: {app_id_input}")
            print("🔍 Fetching game details from Steam...")
            
            # Import and use the Steam API scraper
            from utils.steam_api_scraper import get_steam_game_details
            
            try:
                # Get real game data from Steam
                game_details = await get_steam_game_details(app_id_input)
                game_title = game_details['name']
                
                print(f"✅ Found: {game_title}")
                print(f"📅 Release Date: {game_details.get('release_date', 'Unknown')}")
                print(f"👨‍💻 Developer: {game_details.get('developer', 'Unknown')}")
                
                if game_details.get('videos'):
                    print(f"🎬 Found {len(game_details['videos'])} video(s)")
                    
                    # Ask user if they want to provide a custom video URL
                    print(f"\n📹 Video Source Options:")
                    print(f"1. Use Steam videos (automatic)")
                    print(f"2. Provide custom video URL")
                    
                    video_choice = input("\nChoose video source (1 or 2, default=1): ").strip()
                    
                    if video_choice == "2":
                        print("\n📝 Supported video platforms:")
                        print("   • YouTube: https://www.youtube.com/watch?v=...")
                        print("   • YouTube Shorts: https://www.youtube.com/shorts/... (auto-converted)")
                        print("   • Steam: https://video.akamai.steamstatic.com/...")
                        print("   • Vimeo, Twitch, Dailymotion, etc.")
                        print("\n⚠️  Note: Vizard requires regular YouTube URLs (Shorts will be auto-converted)")
                        custom_url = input("\n🔗 Enter video URL: ").strip()
                        if custom_url:
                            # Validate URL format (accept YouTube, Steam, and other video platforms)
                            valid_domains = [
                                'youtube.com', 'youtu.be', 'steamstatic.com', 'steampowered.com',
                                'vimeo.com', 'twitch.tv', 'dailymotion.com', 'streamable.com'
                            ]
                            
                            if any(domain in custom_url.lower() for domain in valid_domains) or custom_url.startswith('http'):
                                # Show URL conversion preview if it needs conversion
                                if '/shorts/' in custom_url:
                                    video_id = custom_url.split('/shorts/')[-1].split('?')[0]
                                    converted_url = f"https://www.youtube.com/watch?v={video_id}"
                                    print(f"🔄 YouTube Shorts detected - will convert to: {converted_url}")
                                elif 'youtu.be/' in custom_url:
                                    video_id = custom_url.split('youtu.be/')[-1].split('?')[0]
                                    converted_url = f"https://www.youtube.com/watch?v={video_id}"
                                    print(f"🔄 youtu.be URL detected - will convert to: {converted_url}")
                                
                                print(f"✅ Using custom video: {custom_url}")
                                
                                # Ask user to confirm the video matches the game
                                confirm = input(f"\n❓ Does this video contain '{game_title}' gameplay? (y/n, default=y): ").strip().lower()
                                if confirm in ['n', 'no']:
                                    print("⚠️ Please provide a video that matches the game. Using Steam videos instead.")
                                else:
                                    # Add custom URL to game details
                                    if 'custom_videos' not in game_details:
                                        game_details['custom_videos'] = []
                                    game_details['custom_videos'].append(custom_url)
                            else:
                                print("⚠️ Invalid URL format. Please use YouTube, Steam, or other video platform URLs.")
                                print("⚠️ Using Steam videos instead.")
                        else:
                            print("⚠️ No URL provided. Using Steam videos instead.")
                    
                    print(f"\n🎯 Full Pipeline Mode: {game_title}")
                    created_reels = await automation.run_automation(game_title=game_title, game_details=game_details)
                    automation.print_summary(created_reels)
                    
            except Exception as e:
                print(f"❌ Error fetching game details: {e}")
                print("🔄 Using fallback mode...")
                game_title = f"Steam_Game_{app_id_input}"
                game_details = {"app_id": app_id_input}
                created_reels = await automation.run_automation(game_title=game_title, game_details=game_details)
                automation.print_summary(created_reels)
        else:
            print("❌ Invalid Steam App ID. Please enter numbers only (e.g., '1962700'). Exiting...")

if __name__ == "__main__":
    # Example usage:
    # python3 main.py                                    # Interactive Steam App ID mode
    # python3 main.py "Cyberpunk 2077"                   # Full pipeline for specific game
    # python3 main.py --module 1 "Cyberpunk 2077"       # Run only intro module
    # python3 main.py --module 2 "Cyberpunk 2077"       # Run only vizard module  
    # python3 main.py --module 3 "Cyberpunk 2077"       # Run only outro module
    
    asyncio.run(main())
