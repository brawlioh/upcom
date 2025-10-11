#!/usr/bin/env python3
"""
Railway deployment entry point
Preserves all current working settings and configuration
"""
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("🚀 Starting YouTube Reels Automation API (Railway)")
    print("📡 Preserving all local working settings...")
    
    # Import the API server (same as your working local version)
    from api_server import app
    
    # Get port from Railway environment variable
    port = int(os.environ.get("PORT", 8001))
    
    # Start the FastAPI server with same config as local
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        log_level="info",
        access_log=True
    )
