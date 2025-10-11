#!/usr/bin/env python3
"""
Railway deployment entry point
Preserves all current working settings and configuration
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    try:
        print("🚀 Starting YouTube Reels Automation API (Railway)")
        print("📡 Preserving all local working settings...")
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        
        # Import the API server (same as your working local version)
        print("Importing API server...")
        from api_server import app
        print("✅ API server imported successfully")
        
        # Get port from Railway environment variable
        port = int(os.environ.get("PORT", 8001))
        print(f"Starting server on port {port}")
        
        # Start the FastAPI server with same config as local
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port, 
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
