#!/usr/bin/env python3
"""
Batch Processing Example for YouTube Reels Automation

This script demonstrates how to create multiple reels for different games
with various configurations and scheduling options.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from main import YouTubeReelsAutomation
from config import Config
from loguru import logger

class BatchProcessor:
    def __init__(self):
        self.automation = YouTubeReelsAutomation()
        
    async def process_specific_games(self, game_list: list) -> list:
        """Process a specific list of games"""
        logger.info(f"Processing {len(game_list)} specific games")
        
        created_reels = []
        for game_title in game_list:
            try:
                logger.info(f"Creating reel for: {game_title}")
                reel_paths = await self.automation.run_automation(game_title=game_title)
                if reel_paths:
                    created_reels.extend(reel_paths)
                    logger.info(f"✅ Successfully created reel for {game_title}")
                else:
                    logger.warning(f"❌ Failed to create reel for {game_title}")
                
                # Add delay between games to avoid API rate limits
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error processing {game_title}: {e}")
                continue
        
        return created_reels
    
    async def process_trending_batch(self, count: int = 5) -> list:
        """Process trending games in batch"""
        logger.info(f"Processing {count} trending games")
        
        try:
            created_reels = await self.automation.run_automation(count=count)
            logger.info(f"✅ Successfully created {len(created_reels)} reels from trending games")
            return created_reels
        except Exception as e:
            logger.error(f"Error processing trending batch: {e}")
            return []
    
    async def process_with_custom_timing(self, games: list, delay_minutes: int = 5) -> list:
        """Process games with custom timing between each"""
        logger.info(f"Processing {len(games)} games with {delay_minutes}min delays")
        
        created_reels = []
        for i, game_title in enumerate(games):
            try:
                logger.info(f"[{i+1}/{len(games)}] Processing: {game_title}")
                reel_paths = await self.automation.run_automation(game_title=game_title)
                if reel_paths:
                    created_reels.extend(reel_paths)
                
                # Add custom delay (except for last game)
                if i < len(games) - 1:
                    delay_seconds = delay_minutes * 60
                    logger.info(f"Waiting {delay_minutes} minutes before next game...")
                    await asyncio.sleep(delay_seconds)
                
            except Exception as e:
                logger.error(f"Error processing {game_title}: {e}")
                continue
        
        return created_reels

async def main():
    """Main batch processing examples"""
    processor = BatchProcessor()
    
    print("🎬 YouTube Reels Batch Processing Examples")
    print("=" * 50)
    
    # Example 1: Process specific high-priority games
    priority_games = [
        "Cyberpunk 2077",
        "The Elder Scrolls VI", 
        "Grand Theft Auto VI",
        "Starfield",
        "Diablo IV"
    ]
    
    print("\n📋 Example 1: Processing Priority Games")
    priority_reels = await processor.process_specific_games(priority_games[:3])  # Process first 3
    
    # Example 2: Process trending games
    print("\n📈 Example 2: Processing Trending Games")
    trending_reels = await processor.process_trending_batch(count=2)
    
    # Example 3: Process with custom timing
    custom_games = [
        "Halo Infinite",
        "Call of Duty: Modern Warfare III"
    ]
    
    print("\n⏰ Example 3: Processing with Custom Timing")
    custom_reels = await processor.process_with_custom_timing(custom_games, delay_minutes=2)
    
    # Summary
    all_reels = priority_reels + trending_reels + custom_reels
    processor.automation.print_summary(all_reels)
    
    print(f"\n🎯 Batch Processing Complete!")
    print(f"Total reels created: {len(all_reels)}")

if __name__ == "__main__":
    asyncio.run(main())
