#!/usr/bin/env python3
"""
Simple runner for TOR Analysis System
This version skips complex dependencies and runs with basic features
"""

import sys
import subprocess
import os

def check_and_install_requirements():
    """Check and install minimal requirements"""
    minimal_packages = [
        'fastapi',
        'uvicorn',
        'jinja2', 
        'python-multipart',
        'pydantic',
        'pymongo',
        'redis',
        'requests',
        'aiohttp',
        'python-dotenv'
    ]
    
    print("🔧 Checking minimal requirements...")
    
    for package in minimal_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def run_application():
    """Run the FastAPI application"""
    print("\n🚀 Starting TOR Analysis System...")
    print("📍 Access at: http://localhost:8000")
    print("🔑 Login: admin / admin123")
    print("\n" + "="*50)
    
    # Set environment variables
    os.environ.setdefault('PYTHONPATH', '.')
    
    # Run uvicorn
    subprocess.run([
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--reload', 
        '--host', '0.0.0.0', 
        '--port', '8000'
    ])

if __name__ == "__main__":
    try:
        check_and_install_requirements()
        run_application()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try using Docker instead:")
        print("   docker-compose up -d")