import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    HEYGEN_API_KEY = os.getenv('HEYGEN_API_KEY')
    VIZARD_API_KEY = os.getenv('VIZARD_API_KEY')
    CREATOMATE_API_KEY = os.getenv('CREATOMATE_API_KEY')
    
    # Paths
    DATA_PATH = Path(os.getenv('STREAMGANK_DATA_PATH', './data'))
    ASSETS_PATH = DATA_PATH / 'assets'
    VIDEOS_PATH = DATA_PATH / 'videos'
    OUTPUTS_PATH = DATA_PATH / 'outputs'
    
    # Video Settings
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    VIDEO_FPS = 30
    
    # Steam URLs
    STEAM_UPCOMING_URL = "https://store.steampowered.com/search/?filter=popularcomingsoon&os=win"
    STEAM_WISHLIST_URL = "https://steamdb.info/stats/mostwished/"
    
    # Vizard Settings
    VIZARD_USE_WEBHOOK = True  # Set to False to use polling only
    VIZARD_WEBHOOK_TIMEOUT = 120  # seconds
    VIZARD_POLLING_TIMEOUT = 1800  # 30 minutes
    
    # HeyGen Settings
    HEYGEN_BASE_URL = "https://api.heygen.com/v2"
    
    # Vizard Settings
    VIZARD_BASE_URL = "https://api.vizard.ai/v1"
    
    # Creatomate Settings
    CREATOMATE_BASE_URL = "https://api.creatomate.com/v1"
    
    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.ASSETS_PATH.mkdir(parents=True, exist_ok=True)
        cls.VIDEOS_PATH.mkdir(parents=True, exist_ok=True)
        cls.OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for each module
        (cls.ASSETS_PATH / 'intros').mkdir(exist_ok=True)
        (cls.ASSETS_PATH / 'vizard').mkdir(exist_ok=True)
        (cls.ASSETS_PATH / 'outros').mkdir(exist_ok=True)
        (cls.OUTPUTS_PATH / 'final_reels').mkdir(exist_ok=True)
