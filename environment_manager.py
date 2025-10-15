#!/usr/bin/env python3
"""
Environment Manager - Automatic Detection and Configuration
Prevents confusion between local development and Railway production
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

class EnvironmentManager:
    def __init__(self):
        self.environment = self.detect_environment()
        self.load_environment_config()
    
    def detect_environment(self):
        """Automatically detect the current environment"""
        # Railway detection
        if os.getenv('RAILWAY_ENVIRONMENT'):
            return 'railway_production'
        
        # Check for Railway-specific environment variables
        railway_indicators = ['RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID', 'RAILWAY_DEPLOYMENT_ID']
        if any(os.getenv(var) for var in railway_indicators):
            return 'railway_production'
        
        # Check if running on Railway domain
        if os.getenv('PORT') and not os.getenv('LOCAL_DEVELOPMENT'):
            return 'railway_production'
        
        # Local development detection
        if os.getenv('LOCAL_DEVELOPMENT') == 'true':
            return 'local_development'
        
        # Default to local if running from known local paths
        cwd = os.getcwd()
        if 'Documents' in cwd or 'Desktop' in cwd or 'Users' in cwd:
            return 'local_development'
        
        return 'local_development'
    
    def load_environment_config(self):
        """Load appropriate environment configuration"""
        if self.environment == 'railway_production':
            self.load_production_config()
        else:
            self.load_development_config()
    
    def load_production_config(self):
        """Load Railway production configuration"""
        print("🚀 RAILWAY PRODUCTION MODE DETECTED")
        print("📡 Using production API endpoints and settings")
        
        # Set production environment variables
        os.environ['NODE_ENV'] = 'production'
        os.environ['ENVIRONMENT'] = 'railway_production'
        os.environ['USE_PRODUCTION_API'] = 'true'
        os.environ['DEBUG_MODE'] = 'false'
        os.environ['LOG_LEVEL'] = 'info'
        
        # Railway automatically provides these, but set defaults
        if not os.getenv('PORT'):
            os.environ['PORT'] = '8001'
    
    def load_development_config(self):
        """Load local development configuration"""
        print("🔧 LOCAL DEVELOPMENT MODE DETECTED")
        print("🏠 Using local API endpoints and settings")
        
        # Try to load development-specific env file first
        env_files = ['.env.development', '.env.local', '.env']
        for env_file in env_files:
            if os.path.exists(env_file):
                load_dotenv(env_file)
                print(f"✅ Loaded {env_file}")
                break
        else:
            print("⚠️  No development environment file found")
        
        # Set development environment variables
        os.environ['NODE_ENV'] = 'development'
        os.environ['ENVIRONMENT'] = 'local_development'
        os.environ['LOCAL_DEVELOPMENT'] = 'true'
        os.environ['USE_PRODUCTION_API'] = 'false'
        os.environ['DEBUG_MODE'] = 'true'
        os.environ['LOG_LEVEL'] = 'debug'
        
        # Local development defaults
        if not os.getenv('API_PORT'):
            os.environ['API_PORT'] = '8001'
    
    def get_api_server_module(self):
        """Get the appropriate API server module"""
        if self.environment == 'railway_production':
            return 'api_server_production'
        else:
            return 'api_server'
    
    def get_startup_message(self):
        """Get environment-specific startup message"""
        if self.environment == 'railway_production':
            return {
                'title': '🚀 RAILWAY PRODUCTION',
                'description': 'Real APIs • Production Database • Public Access',
                'color': 'red',
                'warnings': [
                    '⚠️  PRODUCTION MODE - Real API calls will be made',
                    '💰 API usage will be charged to your accounts',
                    '🌐 Service is publicly accessible'
                ]
            }
        else:
            return {
                'title': '🔧 LOCAL DEVELOPMENT',
                'description': 'Safe Testing • Local Database • Private Access',
                'color': 'green',
                'warnings': [
                    '✅ Safe for testing and development',
                    '🔄 Auto-reload enabled for code changes',
                    '🏠 Only accessible from localhost'
                ]
            }
    
    def print_environment_info(self):
        """Print detailed environment information"""
        info = self.get_startup_message()
        
        print("\n" + "="*60)
        print(f"{info['title']}")
        print(f"{info['description']}")
        print("="*60)
        
        for warning in info['warnings']:
            print(warning)
        
        print(f"\n📍 Environment: {self.environment}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"📁 Working Directory: {os.getcwd()}")
        print(f"🔧 API Server Module: {self.get_api_server_module()}")
        print("="*60 + "\n")

# Global environment manager instance
env_manager = EnvironmentManager()

def get_environment():
    """Get current environment"""
    return env_manager.environment

def is_production():
    """Check if running in production"""
    return env_manager.environment == 'railway_production'

def is_development():
    """Check if running in development"""
    return env_manager.environment == 'local_development'

def get_api_server_module():
    """Get appropriate API server module"""
    return env_manager.get_api_server_module()
