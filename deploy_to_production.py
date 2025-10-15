#!/usr/bin/env python3
"""
Safe Production Deployment Script
Ensures proper testing before Railway deployment
"""
import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_git_status():
    """Check if there are uncommitted changes"""
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return len(result.stdout.strip()) == 0

def main():
    print("\n" + "="*60)
    print("🚀 SAFE PRODUCTION DEPLOYMENT")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists('railway_main.py'):
        print("❌ ERROR: Not in project root directory")
        print("📁 Please run this from the project root")
        sys.exit(1)
    
    # Check git status
    print("\n1️⃣ CHECKING GIT STATUS")
    if not check_git_status():
        print("⚠️  You have uncommitted changes")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("❌ Deployment cancelled")
            sys.exit(1)
    else:
        print("✅ Git working directory is clean")
    
    # Optional: Run local tests
    print("\n2️⃣ PRE-DEPLOYMENT CHECKS")
    print("🔍 Checking environment configuration...")
    
    # Check if critical files exist
    critical_files = [
        'api_server_production.py',
        'railway_main.py',
        'environment_manager.py',
        'requirements.txt'
    ]
    
    for file in critical_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            sys.exit(1)
    
    # Show current branch
    result = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True)
    current_branch = result.stdout.strip()
    print(f"📍 Current branch: {current_branch}")
    
    if current_branch != 'production':
        print("⚠️  You're not on the production branch")
        response = input("Switch to production branch? (y/N): ")
        if response.lower() == 'y':
            if not run_command("git checkout production", "Switching to production branch"):
                sys.exit(1)
        else:
            print("❌ Deployment cancelled")
            sys.exit(1)
    
    # Confirm deployment
    print("\n3️⃣ DEPLOYMENT CONFIRMATION")
    print("🚨 This will deploy to Railway PRODUCTION")
    print("💰 Real API calls will be made and charged")
    print("🌐 Changes will be publicly accessible")
    
    response = input("\n🚀 Deploy to Railway production? (y/N): ")
    if response.lower() != 'y':
        print("❌ Deployment cancelled")
        sys.exit(1)
    
    # Deploy
    print("\n4️⃣ DEPLOYING TO RAILWAY")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add and commit any final changes
    if not check_git_status():
        commit_msg = f"deploy: Production deployment {timestamp}"
        if run_command("git add .", "Adding changes"):
            if run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
                print("✅ Changes committed")
    
    # Push to production
    if run_command("git push origin production", "Pushing to Railway"):
        print("\n🎉 DEPLOYMENT INITIATED!")
        print("📊 Monitor deployment in Railway dashboard")
        print("⏰ Deployment typically takes 2-5 minutes")
        print("🔗 Check your Railway URLs once deployment completes")
        
        # Show Railway URLs (if available)
        print("\n📋 RAILWAY SERVICES:")
        print("  🔧 Backend: Check Railway dashboard for URL")
        print("  🎨 Frontend: Check Railway dashboard for URL")
        
    else:
        print("❌ Deployment failed")
        sys.exit(1)
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
