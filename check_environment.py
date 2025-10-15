#!/usr/bin/env python3
"""
Environment Status Checker
Quick tool to verify current environment configuration
"""
import os
import sys
from environment_manager import env_manager

def main():
    print("\n" + "="*60)
    print("🔍 ENVIRONMENT STATUS CHECK")
    print("="*60)
    
    # Environment detection
    env_manager.print_environment_info()
    
    # Check critical settings
    print("🔧 CRITICAL SETTINGS:")
    print(f"  NODE_ENV: {os.getenv('NODE_ENV', 'Not set')}")
    print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT', 'Not set')}")
    print(f"  LOCAL_DEVELOPMENT: {os.getenv('LOCAL_DEVELOPMENT', 'Not set')}")
    print(f"  USE_PRODUCTION_API: {os.getenv('USE_PRODUCTION_API', 'Not set')}")
    print(f"  PORT: {os.getenv('PORT', 'Not set')}")
    
    # Check Railway indicators
    print("\n🚀 RAILWAY INDICATORS:")
    railway_vars = [
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_PROJECT_ID', 
        'RAILWAY_SERVICE_ID',
        'RAILWAY_DEPLOYMENT_ID'
    ]
    
    for var in railway_vars:
        value = os.getenv(var)
        status = "✅ SET" if value else "❌ NOT SET"
        print(f"  {var}: {status}")
    
    # Check API keys (without revealing them)
    print("\n🔑 API KEYS STATUS:")
    api_keys = [
        'OPENAI_API_KEY',
        'HEYGEN_API_KEY', 
        'VIZARD_API_KEY',
        'CREATOMATE_API_KEY',
        'CLOUDINARY_CLOUD_NAME'
    ]
    
    for key in api_keys:
        value = os.getenv(key)
        if value:
            print(f"  {key}: ✅ SET ({len(value)} chars)")
        else:
            print(f"  {key}: ❌ NOT SET")
    
    # Recommended actions
    print("\n📋 RECOMMENDED ACTIONS:")
    if env_manager.environment == 'railway_production':
        print("  🚀 You're in PRODUCTION mode")
        print("  ✅ Use Railway dashboard to manage settings")
        print("  ⚠️  All API calls will be real and charged")
    else:
        print("  🔧 You're in DEVELOPMENT mode")
        print("  ✅ Safe for testing and development")
        print("  📝 Create .env.development for local settings")
        print("  🚀 Use 'python3 start_development.py' to start")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
