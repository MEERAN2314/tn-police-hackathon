#!/usr/bin/env python3
"""
Simple startup script for TOR Analysis System
This version works without complex dependencies
"""

import sys
import os
import subprocess
import time

def install_basic_requirements():
    """Install only the essential packages"""
    basic_packages = [
        'fastapi',
        'uvicorn',
        'jinja2',
        'python-multipart',
        'python-dotenv'
    ]
    
    print("📦 Installing basic requirements...")
    for package in basic_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - already installed")
        except ImportError:
            print(f"📥 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def run_app():
    """Run the simplified application"""
    print("\n🚀 Starting TOR Analysis System (Simplified Version)...")
    print("📍 Dashboard: http://localhost:8000")
    print("🔑 Login: admin / admin123")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Set environment
    os.environ.setdefault('PYTHONPATH', '.')
    
    try:
        # Run the working version
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main_working:app', 
            '--reload', 
            '--host', '0.0.0.0', 
            '--port', '8000'
        ])
    except Exception as e:
        print(f"❌ Error running app: {e}")
        print("\n💡 Try running directly:")
        print("python -m uvicorn app.main_working:app --reload")

if __name__ == "__main__":
    try:
        print("🔧 TOR Analysis System - Simple Setup")
        print("="*50)
        
        # Install basic requirements
        install_basic_requirements()
        
        # Small delay
        time.sleep(1)
        
        # Run the app
        run_app()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down TOR Analysis System...")
        print("Thank you for using our system!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Alternative: Try running directly:")
        print("python -m uvicorn app.main_working:app --reload --host 0.0.0.0 --port 8000")