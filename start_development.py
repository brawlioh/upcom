#!/usr/bin/env python3
"""
Development Environment Startup Script - LOCAL ONLY
Use this for local testing and development
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv
from environment_manager import env_manager

def main():
    # Print environment information
    env_manager.print_environment_info()
    
    # Ensure we're in development mode
    if env_manager.environment == 'railway_production':
        print("❌ ERROR: This script should not run in Railway production!")
        print("🚀 Railway automatically uses railway_main.py")
        sys.exit(1)
    
    # Force local development mode
    os.environ['LOCAL_DEVELOPMENT'] = 'true'
    
    # Import the DEVELOPMENT API server (with all validation)
    print("Importing DEVELOPMENT API server...")
    from api_server import app
    print("✅ DEVELOPMENT API server imported successfully")
    
    # Start the FastAPI server for development
    port = int(os.environ.get("API_PORT", 8001))
    print(f"🚀 Starting development server on http://localhost:{port}")
    print("🔍 Validation system: ENABLED")
    print("🎯 Steam App ID validation: ACTIVE")
    print("📊 All features available for testing")
    
    uvicorn.run(
        app, 
        host="127.0.0.1",  # Local only for development
        port=port, 
        log_level="debug",
        reload=True,  # Auto-reload on code changes
        access_log=True
    )

if __name__ == "__main__":
    main()
