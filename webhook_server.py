#!/usr/bin/env python3
"""
Vizard Webhook Server
Receives notifications from Vizard.ai when video processing completes or fails
"""

import asyncio
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import threading
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store webhook notifications in memory (you could use Redis/database for production)
webhook_notifications = {}

@app.route('/vizard/webhook', methods=['POST'])
def vizard_webhook():
    """Handle Vizard webhook notifications"""
    try:
        # Get the webhook payload
        payload = request.get_json()
        
        if not payload:
            logger.error("No JSON payload received")
            return jsonify({"error": "No JSON payload"}), 400
        
        # Log the received webhook
        logger.info(f"📥 Vizard webhook received: {json.dumps(payload, indent=2)}")
        
        # Extract key information
        project_id = payload.get('projectId') or payload.get('project_id')
        status = payload.get('status')
        code = payload.get('code')
        error_msg = payload.get('errMsg') or payload.get('error_message')
        
        if not project_id:
            logger.error("No project_id found in webhook payload")
            return jsonify({"error": "Missing project_id"}), 400
        
        # Store the notification
        notification_data = {
            'timestamp': datetime.now().isoformat(),
            'payload': payload,
            'project_id': project_id,
            'status': status,
            'code': code,
            'error_msg': error_msg,
            'processed': False
        }
        
        webhook_notifications[project_id] = notification_data
        
        # Log status
        if code == 4008:
            logger.error(f"❌ Vizard failed for project {project_id}: {error_msg}")
        elif status == 'completed' or code == 200:
            logger.info(f"✅ Vizard completed for project {project_id}")
        else:
            logger.info(f"📊 Vizard status update for project {project_id}: {status} (code: {code})")
        
        return jsonify({"status": "received", "project_id": project_id}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/vizard/status/<project_id>', methods=['GET'])
def get_project_status(project_id):
    """Get status for a specific project"""
    if project_id in webhook_notifications:
        return jsonify(webhook_notifications[project_id])
    else:
        return jsonify({"error": "Project not found"}), 404

@app.route('/vizard/notifications', methods=['GET'])
def get_all_notifications():
    """Get all webhook notifications"""
    return jsonify(webhook_notifications)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

def run_webhook_server():
    """Run the webhook server"""
    logger.info("🚀 Starting Vizard webhook server on http://localhost:5001")
    logger.info("📡 Webhook endpoint: http://localhost:5001/vizard/webhook")
    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == '__main__':
    run_webhook_server()
