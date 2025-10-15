#!/usr/bin/env python3
"""
Development Environment Startup Script
Use this for local testing and development
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

def main():
    print("🔧 Starting YouTube Reels Automation API (DEVELOPMENT MODE)")
    print("📍 Local environment - Safe for testing")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Load development environment variables
    if os.path.exists('.env.development'):
        load_dotenv('.env.development')
        print("✅ Loaded .env.development")
    else:
        load_dotenv()  # Fallback to .env
        print("⚠️  Using .env (create .env.development for better separation)")
    
    # Set development flags
    os.environ['NODE_ENV'] = 'development'
    os.environ['ENVIRONMENT'] = 'development'
    
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
