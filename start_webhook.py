#!/usr/bin/env python3
"""
Start the Vizard webhook server with ngrok tunnel
Run this before running the main automation
"""

import subprocess
import sys
import time
import requests
import json
import threading

ngrok_process = None
webhook_process = None
public_url = None

def check_webhook_server():
    """Check if webhook server is running"""
    try:
        response = requests.get("http://localhost:5001/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_ngrok_public_url():
    """Get the public URL from ngrok"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json()
            for tunnel in tunnels.get('tunnels', []):
                if tunnel.get('proto') == 'https':
                    return tunnel.get('public_url')
        return None
    except:
        return None

def start_ngrok_tunnel():
    """Start ngrok tunnel for webhook server"""
    global ngrok_process, public_url
    
    print("🌐 Starting ngrok tunnel...")
    try:
        # Start ngrok tunnel
        ngrok_process = subprocess.Popen([
            "ngrok", "http", "5001", "--log=stdout"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for ngrok to start
        time.sleep(5)
        
        # Get public URL
        public_url = get_ngrok_public_url()
        if public_url:
            print(f"✅ Ngrok tunnel started: {public_url}")
            return True
        else:
            print("❌ Failed to get ngrok public URL")
            return False
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return False

def start_webhook_server():
    """Start the webhook server"""
    global webhook_process
    
    if check_webhook_server():
        print("✅ Webhook server is already running on http://localhost:5001")
        return True
    
    print("🚀 Starting Vizard webhook server...")
    try:
        # Start webhook server in background
        webhook_process = subprocess.Popen([
            sys.executable, "webhook_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server started successfully
        if check_webhook_server():
            print("✅ Webhook server started successfully!")
            return True
        else:
            print("❌ Failed to start webhook server")
            return False
            
    except Exception as e:
        print(f"❌ Error starting webhook server: {e}")
        return False

def update_vizard_webhook_url():
    """Update the Vizard module with the public webhook URL"""
    if not public_url:
        return False
    
    try:
        webhook_url = f"{public_url}/vizard/webhook"
        
        # Read the current module2_vizard.py
        with open("modules/module2_vizard.py", "r") as f:
            content = f.read()
        
        # Replace localhost webhook URL with public URL
        updated_content = content.replace(
            '"webhookUrl": "http://localhost:5001/vizard/webhook"',
            f'"webhookUrl": "{webhook_url}"'
        )
        
        # Write back the updated content
        with open("modules/module2_vizard.py", "w") as f:
            f.write(updated_content)
        
        print(f"✅ Updated Vizard webhook URL: {webhook_url}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating webhook URL: {e}")
        return False

def cleanup():
    """Clean up processes on exit"""
    global ngrok_process, webhook_process
    
    print("\n🧹 Cleaning up processes...")
    
    if ngrok_process:
        ngrok_process.terminate()
        print("✅ Ngrok tunnel stopped")
    
    if webhook_process:
        webhook_process.terminate()
        print("✅ Webhook server stopped")

if __name__ == "__main__":
    try:
        # Start webhook server
        if not start_webhook_server():
            print("❌ Failed to start webhook server")
            sys.exit(1)
        
        # Start ngrok tunnel
        if not start_ngrok_tunnel():
            print("❌ Failed to start ngrok tunnel")
            cleanup()
            sys.exit(1)
        
        # Update Vizard module with public URL
        if not update_vizard_webhook_url():
            print("❌ Failed to update webhook URL")
            cleanup()
            sys.exit(1)
        
        print("\n" + "="*70)
        print("🎯 WEBHOOK SYSTEM READY!")
        print("="*70)
        print(f"📡 Public Webhook URL: {public_url}/vizard/webhook")
        print(f"🔍 Status Dashboard: {public_url}/vizard/notifications")
        print(f"🏠 Local Server: http://localhost:5001")
        print("="*70)
        print("\n🎯 NEXT STEPS:")
        print("1. ✅ Ngrok tunnel is running")
        print("2. ✅ Webhook server is running") 
        print("3. ✅ Vizard module updated with public URL")
        print("4. 🚀 Run your automation: python3 main.py")
        print("="*70)
        
        # Keep the script running
        print("\n⏳ Press Ctrl+C to stop the webhook system...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down webhook system...")
        cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        cleanup()
        sys.exit(1)
