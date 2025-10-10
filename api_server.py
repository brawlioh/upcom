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

# Import your existing automation system
from main import YouTubeReelsAutomation

app = FastAPI(title="YouTube Reels Automation API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],  # Frontend URLs
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

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

async def update_job_progress(job_id: str, step: int, step_name: str, status: str = "running"):
    """Update job progress and broadcast to connected clients"""
    if job_id in automation_jobs:
        job = automation_jobs[job_id]
        job['current_step'] = step
        job['step_name'] = step_name
        job['status'] = status
        job['progress'] = int((step / job['total_steps']) * 100) if step > 0 else 0
        
        # Broadcast update to all connected clients
        await manager.broadcast(json.dumps({
            'type': 'progress_update',
            'job_id': job_id,
            'data': job
        }))

async def run_automation_job(job_id: str, request: AutomationRequest):
    """Background task to run the automation"""
    try:
        # Update job status to running
        automation_jobs[job_id]['status'] = 'running'
        await update_job_progress(job_id, 0, "Initializing automation system", "running")
        
        # Create automation instance
        automation = YouTubeReelsAutomation()
        
        # Prepare parameters based on request mode
        if request.mode == 'single':
            if not request.game_title:
                raise ValueError("Game title is required for single mode")
            
            await update_job_progress(job_id, 1, "Creating intro video with HeyGen")
            
            # Get game data
            game_data = await automation.get_game_data(request.game_title)
            if not game_data:
                raise ValueError(f"Could not find data for game: {request.game_title}")
            
            # Add custom video URL if provided
            game_details = {}
            if request.custom_video_url:
                game_details['custom_videos'] = [request.custom_video_url]
            
            # Run the automation with progress updates
            result = await run_automation_with_progress(automation, job_id, game_data, game_details)
            
        elif request.mode == 'steam':
            if not request.steam_app_id:
                raise ValueError("Steam App ID is required for steam mode")
            
            await update_job_progress(job_id, 1, "Fetching Steam game details")
            
            # Import Steam API scraper
            from utils.steam_api_scraper import get_steam_game_details
            
            # Get game details from Steam
            game_details = await get_steam_game_details(request.steam_app_id)
            game_title = game_details['name']
            
            # Add custom video URL if provided
            if request.custom_video_url:
                if 'custom_videos' not in game_details:
                    game_details['custom_videos'] = []
                game_details['custom_videos'].append(request.custom_video_url)
            
            # Run the automation
            result = await run_automation_with_progress(automation, job_id, game_title, game_details)
            
        else:
            raise ValueError(f"Invalid mode: {request.mode}. Only 'steam' mode is supported.")
        
        # Job completed successfully
        automation_jobs[job_id]['status'] = 'completed'
        automation_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        automation_jobs[job_id]['result_path'] = result
        automation_jobs[job_id]['progress'] = 100
        
        await manager.broadcast(json.dumps({
            'type': 'job_completed',
            'job_id': job_id,
            'result_path': result
        }))
        
    except Exception as e:
        logger.error(f"Automation job {job_id} failed: {e}")
        automation_jobs[job_id]['status'] = 'failed'
        automation_jobs[job_id]['error_message'] = str(e)
        automation_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
        await manager.broadcast(json.dumps({
            'type': 'job_failed',
            'job_id': job_id,
            'error': str(e)
        }))

async def run_automation_with_progress(automation, job_id: str, game_data, game_details=None):
    """Run automation with progress updates"""
    if isinstance(game_data, str):
        game_title = game_data
        game_dict = game_details or {}
    else:
        game_title = game_data.get('title', 'Unknown Game')
        game_dict = game_data
    
    # Module 1: Intro
    await update_job_progress(job_id, 1, "Creating intro video with HeyGen")
    intro_path = await automation.intro_generator.create_intro(game_title, game_dict)
    
    if not intro_path:
        raise Exception("Module 1 (Intro) failed")
    
    # Module 2: Gameplay
    await update_job_progress(job_id, 2, "Processing gameplay clip with Vizard")
    vizard_path = await automation.vizard_processor.process_gameplay_clip(game_title, game_dict)
    
    if not vizard_path:
        raise Exception("Module 2 (Vizard) failed")
    
    # Module 3: Outro
    await update_job_progress(job_id, 3, "Creating outro video with HeyGen")
    outro_path = await automation.outro_generator.create_outro(game_title, game_dict)
    
    if not outro_path:
        raise Exception("Module 3 (Outro) failed")
    
    # Module 4: Compilation
    await update_job_progress(job_id, 4, "Compiling final reel with Creatomate")
    final_path = await automation.compiler.compile_reel(intro_path, vizard_path, outro_path, game_title)
    
    return final_path

@app.post("/api/automation/start")
async def start_automation(request: AutomationRequest, background_tasks: BackgroundTasks):
    """Start a new automation job"""
    job_id = str(uuid.uuid4())
    
    # Create job record
    automation_jobs[job_id] = {
        'job_id': job_id,
        'status': 'queued',
        'progress': 0,
        'current_step': 0,
        'total_steps': 4,
        'step_name': 'Queued',
        'created_at': datetime.now().isoformat(),
        'request': request.dict()
    }
    
    # Start background task
    background_tasks.add_task(run_automation_job, job_id, request)
    
    return {'job_id': job_id, 'status': 'queued'}

@app.get("/api/automation/status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a specific job"""
    if job_id not in automation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = automation_jobs[job_id]
    
    # If job is completed but frontend might have missed the WebSocket message, broadcast again
    if job['status'] == 'completed' and job.get('result_path'):
        await manager.broadcast(json.dumps({
            'type': 'job_completed',
            'job_id': job_id,
            'result_path': job['result_path'],
            'data': job
        }))
    
    return job

@app.get("/api/automation/jobs")
async def list_jobs():
    """List all jobs"""
    return list(automation_jobs.values())

@app.delete("/api/automation/stop/{job_id}")
async def stop_job(job_id: str):
    """Stop a running job (placeholder - would need proper cancellation logic)"""
    if job_id not in automation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = automation_jobs[job_id]
    if job['status'] == 'running':
        job['status'] = 'cancelled'
        job['completed_at'] = datetime.now().isoformat()
    
    return {'message': 'Job stopped', 'job_id': job_id}

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
        'active_jobs': len([j for j in automation_jobs.values() if j['status'] == 'running']),
        'total_jobs': len(automation_jobs)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
