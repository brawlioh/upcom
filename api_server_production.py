import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
import uvicorn
import os

# Import your existing automation system
from main import YouTubeReelsAutomation

app = FastAPI(title="YouTube Reels Automation API - PRODUCTION", version="1.0.0")

# Add CORS middleware - works for both local and Railway deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002",
        "https://*.railway.app",  # Railway frontend domains
        "*"  # Allow all origins for Railway deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state management
automation_jobs: Dict[str, Dict] = {}
active_connections: List[WebSocket] = []

class AutomationRequest(BaseModel):
    mode: str  # 'steam' only
    game_title: Optional[str] = None
    steam_app_id: Optional[str] = None
    custom_video_url: Optional[str] = None
    count: Optional[int] = 1

class JobStatus(BaseModel):
    job_id: str
    status: str  # 'queued', 'running', 'completed', 'failed'
    progress: int  # 0-100
    current_step: int
    total_steps: int
    step_name: str
    created_at: str
    completed_at: Optional[str] = None
    result_path: Optional[str] = None
    error_message: Optional[str] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

def validate_production_environment():
    """Ensure we're running in production mode with all required API keys"""
    required_keys = ['OPENAI_API_KEY', 'HEYGEN_API_KEY', 'VIZARD_API_KEY', 'CREATOMATE_API_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        raise Exception(f"PRODUCTION ERROR: Missing API keys: {', '.join(missing_keys)}")
    
    logger.info("✅ PRODUCTION MODE: All API keys validated")

# Validate production environment on startup
validate_production_environment()

@app.post("/api/automation/start")
async def start_automation(request: AutomationRequest, background_tasks: BackgroundTasks):
    """Start automation job - PRODUCTION VERSION (Real APIs only)"""
    job_id = str(uuid.uuid4())
    
    # Create job record
    automation_jobs[job_id] = {
        'job_id': job_id,
        'status': 'queued',
        'progress': 0,
        'current_step': 0,
        'total_steps': 4,
        'step_name': 'Initializing...',
        'created_at': datetime.now().isoformat(),
        'request': request.dict()
    }
    
    # Start background task
    background_tasks.add_task(run_automation_job, job_id, request)
    
    logger.info(f"🚀 PRODUCTION: Started automation job {job_id} for {request.mode} mode")
    
    return {"job_id": job_id, "status": "queued"}

async def run_automation_job(job_id: str, request: AutomationRequest):
    """Run automation job with real API calls only"""
    try:
        logger.info(f"🎬 PRODUCTION: Running automation job {job_id}")
        
        # Initialize automation
        automation = YouTubeReelsAutomation()
        
        # Update job status
        automation_jobs[job_id]['status'] = 'running'
        await manager.broadcast(json.dumps({
            'type': 'job_started',
            'job_id': job_id
        }))
        
        if request.mode == 'steam':
            # Get game details
            game_title = request.game_title or f"Steam_Game_{request.steam_app_id}"
            game_details = {}
            
            if request.steam_app_id:
                game_details = automation.steam_scraper.get_game_details(request.steam_app_id)
                if game_details:
                    game_title = game_details.get('title', game_title)
            
            # Add custom video URL if provided
            if request.custom_video_url:
                if 'custom_videos' not in game_details:
                    game_details['custom_videos'] = []
                game_details['custom_videos'].append(request.custom_video_url)
            
            # Run the automation with REAL APIs ONLY
            result = await run_automation_with_progress(automation, job_id, game_title, game_details)
            
        else:
            raise ValueError(f"Invalid mode: {request.mode}. Only 'steam' mode is supported.")
        
        # Job completed successfully - NO SIMULATION URLs
        automation_jobs[job_id]['status'] = 'completed'
        automation_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        automation_jobs[job_id]['result_path'] = result
        automation_jobs[job_id]['progress'] = 100
        
        # PRODUCTION: Only return real file paths, no fake URLs
        logger.info(f"✅ PRODUCTION: Job {job_id} completed with real result: {result}")
        
        await manager.broadcast(json.dumps({
            'type': 'job_completed',
            'job_id': job_id,
            'result_path': result
        }))
        
    except Exception as e:
        logger.error(f"❌ PRODUCTION: Automation job {job_id} failed: {e}")
        automation_jobs[job_id]['status'] = 'failed'
        automation_jobs[job_id]['error_message'] = str(e)
        automation_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
        await manager.broadcast(json.dumps({
            'type': 'job_failed',
            'job_id': job_id,
            'error': str(e)
        }))

async def run_automation_with_progress(automation, job_id: str, game_data, game_details=None):
    """Run automation with progress updates - PRODUCTION VERSION"""
    if isinstance(game_data, str):
        game_title = game_data
        game_dict = game_details or {}
    else:
        game_title = game_data.get('title', 'Unknown Game')
        game_dict = game_data
    
    logger.info(f"🎬 PRODUCTION: Starting automation for {game_title}")
    
    # Module 1: Intro (Real HeyGen API)
    await update_job_progress(job_id, 1, "Creating intro video with HeyGen (Real API)")
    intro_path = await automation.intro_generator.create_intro(game_title, game_dict)
    
    if not intro_path:
        raise Exception("Module 1 (Intro) failed - Real HeyGen API error")
    
    logger.info(f"✅ PRODUCTION: Module 1 completed: {intro_path}")
    
    # Module 2: Gameplay (Real Vizard API)
    await update_job_progress(job_id, 2, "Processing gameplay clip with Vizard (Real API)")
    vizard_path = await automation.vizard_processor.process_gameplay_clip(game_title, game_dict)
    
    if not vizard_path:
        raise Exception("Module 2 (Gameplay) failed - Real Vizard API error")
    
    logger.info(f"✅ PRODUCTION: Module 2 completed: {vizard_path}")
    
    # Module 3: Outro (Real HeyGen API)
    await update_job_progress(job_id, 3, "Creating outro video with HeyGen (Real API)")
    outro_path = await automation.outro_generator.create_outro(game_title, game_dict)
    
    if not outro_path:
        raise Exception("Module 3 (Outro) failed - Real HeyGen API error")
    
    logger.info(f"✅ PRODUCTION: Module 3 completed: {outro_path}")
    
    # Module 4: Compilation (Real Creatomate API)
    await update_job_progress(job_id, 4, "Compiling final reel with Creatomate (Real API)")
    final_path = await automation.compiler.compile_reel(intro_path, vizard_path, outro_path, game_title)
    
    if not final_path:
        raise Exception("Module 4 (Compilation) failed - Real Creatomate API error")
    
    logger.info(f"✅ PRODUCTION: All modules completed successfully: {final_path}")
    
    return final_path

async def update_job_progress(job_id: str, step: int, step_name: str):
    """Update job progress"""
    if job_id in automation_jobs:
        automation_jobs[job_id]['current_step'] = step
        automation_jobs[job_id]['step_name'] = step_name
        automation_jobs[job_id]['progress'] = int((step / 4) * 100)
        
        await manager.broadcast(json.dumps({
            'type': 'progress_update',
            'job_id': job_id,
            'step': step,
            'step_name': step_name,
            'progress': automation_jobs[job_id]['progress']
        }))

@app.get("/api/automation/status/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    if job_id not in automation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = automation_jobs[job_id]
    
    # If job is completed, broadcast again in case frontend missed it
    if job['status'] == 'completed' and job.get('result_path'):
        await manager.broadcast(json.dumps({
            'type': 'job_completed',
            'job_id': job_id,
            'result_path': job['result_path'],
            'data': job
        }))
    
    return job

@app.get("/api/automation/jobs")
async def get_all_jobs():
    """Get all jobs"""
    return list(automation_jobs.values())

@app.delete("/api/automation/stop/{job_id}")
async def stop_job(job_id: str):
    """Stop a running job"""
    if job_id not in automation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    automation_jobs[job_id]['status'] = 'cancelled'
    automation_jobs[job_id]['completed_at'] = datetime.now().isoformat()
    
    await manager.broadcast(json.dumps({
        'type': 'job_cancelled',
        'job_id': job_id
    }))
    
    return {"message": f"Job {job_id} cancelled"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'mode': 'PRODUCTION',
        'simulation': False,
        'active_jobs': len([j for j in automation_jobs.values() if j['status'] == 'running']),
        'total_jobs': len(automation_jobs),
        'environment': 'production',
        'version': '1.0.0'
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        'message': 'YouTube Reels Automation API - PRODUCTION MODE',
        'status': 'running',
        'simulation': False,
        'docs': '/docs'
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
