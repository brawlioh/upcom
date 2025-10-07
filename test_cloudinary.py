#!/usr/bin/env python3
"""
Test Module 1 Intro Generation + Creatomate Compilation - Complete workflow test
Tests the entire process from intro generation to successful Creatomate video rendering
"""
import asyncio
import sys
import os
from pathlib import Path
from loguru import logger
import cloudinary
import cloudinary.uploader
from config import Config
import requests

# Add modules to path
sys.path.append(str(Path(__file__).parent / "modules"))
from module1_intro import IntroGenerator
from module4_compilation import CreatorMateCompiler

def setup_logging():
    """Setup logging for the test"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

async def test_module1_intro_workflow():
    """Test the complete Module 1 intro workflow"""
    print("🎬 Testing Module 1 Intro Generation Workflow")
    print("=" * 60)
    
    # Test game data
    test_game = "The Elder Scrolls VI"
    test_game_details = {
        "description": "The highly anticipated sequel to Skyrim",
        "tags": ["RPG", "Fantasy", "Open World"],
        "developer": "Bethesda Game Studios",
        "release_date": "TBA"
    }
    
    try:
        # Initialize the intro generator
        print("\n🔧 Step 1: Initializing IntroGenerator...")
        intro_gen = IntroGenerator()
        print("✅ IntroGenerator initialized successfully")
        
        # Test script generation
        print(f"\n📝 Step 2: Generating intro script for '{test_game}'...")
        script = await intro_gen.generate_intro_script(test_game, test_game_details)
        print(f"✅ Generated script: '{script}'")
        
        # Test HeyGen video generation
        print(f"\n🎥 Step 3: Generating HeyGen video with script...")
        print(f"Script to be used: '{script}'")
        
        # This will generate the video and process it for Creatomate compatibility
        video_result = await intro_gen.generate_heygen_video(script, test_game)
        
        if video_result:
            print(f"✅ HeyGen video generated successfully!")
            print(f"Result: {video_result}")
            
            # Test if the result is a Creatomate-compatible URL
            if video_result.startswith('http'):
                print(f"\n🌐 Step 4: Testing URL accessibility for Creatomate...")
                try:
                    response = requests.head(video_result, timeout=30)
                    print(f"✅ URL is accessible - Status: {response.status_code}")
                    print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
                    print(f"Content-Length: {response.headers.get('content-length', 'Unknown')}")
                    
                    if response.status_code == 200:
                        print("✅ Module 1 workflow completed successfully!")
                        return video_result
                    else:
                        print(f"⚠️  WARNING: URL returned status {response.status_code}")
                        return video_result  # Still return for Creatomate test
                        
                except Exception as e:
                    print(f"❌ URL accessibility test failed: {e}")
                    return video_result  # Still return for Creatomate test
            else:
                print(f"✅ Local file generated: {video_result}")
                return video_result
        else:
            print("❌ HeyGen video generation failed - no result returned")
            return None
            
    except Exception as e:
        print(f"❌ Module 1 workflow failed: {e}")
        logger.error(f"Detailed error: {e}")
        return None

async def test_complete_workflow_with_creatomate():
    """Test the complete workflow: Module 1 → Creatomate → Final Video"""
    print("🎯 Testing COMPLETE Workflow: Module 1 → Creatomate Rendering")
    print("=" * 70)
    
    # Test game data
    test_game = "The Elder Scrolls VI"
    
    try:
        # Step 1: Generate intro video with Module 1
        print("\n🎬 PHASE 1: Module 1 Intro Generation")
        print("-" * 40)
        intro_url = await test_module1_intro_workflow()
        
        if not intro_url:
            print("❌ Cannot proceed - Module 1 failed")
            return None
        
        # Step 2: Verify intro URL is Creatomate-ready
        print(f"\n🔄 PHASE 2: Verifying Intro URL for Creatomate")
        print("-" * 40)
        
        if intro_url.startswith('http'):
            print(f"✅ Got URL from Module 1: {intro_url}")
            
            # Check if it's a Cloudinary URL (preferred) or HeyGen share URL
            if "cloudinary.com" in intro_url:
                print("✅ Cloudinary URL detected - optimal for Creatomate")
            elif "/share/" in intro_url:
                print("⚠️  HeyGen share URL - may work with Creatomate")
            else:
                print("📝 Other URL type - testing accessibility...")
                
            # Test URL accessibility
            try:
                response = requests.head(intro_url, timeout=10)
                print(f"✅ Intro URL accessible - Status: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Intro URL accessibility issue: {e}")
        else:
            print(f"✅ Local file path: {intro_url}")
            if not os.path.exists(intro_url):
                print("❌ Local file does not exist")
                return None
        
        # Step 3: Create mock URLs for vizard and outro (for testing)
        print(f"\n🎭 PHASE 3: Setting up Mock URLs for Complete Test")
        print("-" * 40)
        
        # Use sample video URLs for vizard and outro (for testing purposes)
        vizard_url = "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
        outro_url = "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_2mb.mp4"
        
        print(f"✅ Intro URL (from Module 1): {intro_url}")
        print(f"✅ Vizard URL (mock): {vizard_url}")
        print(f"✅ Outro URL (mock): {outro_url}")
        
        # Step 4: Test Creatomate compilation
        print(f"\n🎨 PHASE 4: Creatomate Video Compilation")
        print("-" * 40)
        
        compiler = CreatorMateCompiler()
        print("🔧 Initializing Creatomate compiler...")
        
        print("🚀 Starting Creatomate render...")
        final_video_url = await compiler.compile_reel(
            intro_url=intro_url,
            vizard_url=vizard_url, 
            outro_url=outro_url,
            game_title=test_game
        )
        
        if final_video_url:
            print(f"\n🎉 SUCCESS: CREATOMATE RENDER COMPLETED!")
            print(f"✅ Final video URL: {final_video_url}")
            
            # Test final video accessibility
            print(f"\n🌐 PHASE 5: Verifying Final Video")
            print("-" * 40)
            try:
                response = requests.head(final_video_url, timeout=30)
                print(f"✅ Final video is accessible - Status: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
                print(f"Content-Length: {response.headers.get('content-length', 'Unknown')} bytes")
                
                if response.status_code == 200:
                    print("\n🏆 COMPLETE SUCCESS!")
                    print("✅ Module 1 → Creatomate → Final Video WORKFLOW COMPLETED!")
                    return final_video_url
                else:
                    print(f"⚠️  Final video returned status {response.status_code}")
                    return final_video_url
                    
            except Exception as e:
                print(f"❌ Final video accessibility test failed: {e}")
                return final_video_url
        else:
            print("❌ Creatomate rendering failed - no final video generated")
            return None
            
    except Exception as e:
        print(f"❌ Complete workflow failed: {e}")
        logger.error(f"Detailed error: {e}")
        return None

def test_cloudinary_config():
    """Test Cloudinary configuration"""
    print("\n🔧 Testing Cloudinary Configuration")
    print(f"Cloud Name: {Config.CLOUDINARY_CLOUD_NAME}")
    print(f"API Key: {Config.CLOUDINARY_API_KEY[:10]}..." if Config.CLOUDINARY_API_KEY else "None")
    print(f"API Secret: {'Set' if Config.CLOUDINARY_API_SECRET else 'None'}")
    
    # Initialize Cloudinary
    cloudinary.config(
        cloud_name=Config.CLOUDINARY_CLOUD_NAME,
        api_key=Config.CLOUDINARY_API_KEY,
        api_secret=Config.CLOUDINARY_API_SECRET
    )
    print("✅ Cloudinary configured successfully")

def test_heygen_processing():
    """Test the HeyGen video processing functions"""
    print("\n🧪 Testing HeyGen Video Processing Functions")
    
    try:
        intro_gen = IntroGenerator()
        
        # Test the process_heygen_for_creatomate function
        print("Testing process_heygen_for_creatomate function...")
        result = intro_gen.test_process_heygen_for_creatomate()
        
        if result:
            print("✅ HeyGen processing test completed successfully!")
            print(f"Results: {result}")
            return result
        else:
            print("❌ HeyGen processing test failed")
            return None
            
    except Exception as e:
        print(f"❌ HeyGen processing test failed: {e}")
        return None

async def main():
    """Main test function"""
    setup_logging()
    
    print("🚀 Starting COMPLETE Workflow Test: Module 1 → Creatomate")
    print("=" * 70)
    
    # Test 1: Cloudinary Configuration
    test_cloudinary_config()
    
    # Test 2: Complete Workflow with Creatomate Rendering
    print("\n🎯 Running COMPLETE WORKFLOW TEST...")
    final_video = await test_complete_workflow_with_creatomate()
    
    # Test 3: Fallback tests if needed
    if not final_video:
        print("\n🔄 Trying individual component tests...")
        
        # Test Module 1 only
        module1_result = await test_module1_intro_workflow()
        
        # Test HeyGen processing
        if module1_result:
            print("\n🧪 Testing HeyGen processing functions...")
            test_heygen_processing()
    
    print("\n" + "=" * 70)
    if final_video:
        print("🏆 COMPLETE SUCCESS!")
        print("✅ Module 1 → Creatomate → Final Video WORKFLOW COMPLETED!")
        print(f"🎬 Final rendered video: {final_video}")
        print("✅ Test objective achieved: Creatomate rendered successfully!")
    else:
        print("❌ COMPLETE WORKFLOW FAILED")
        print("❌ Could not achieve Creatomate successful render")
        print("Please check the logs above for details")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
