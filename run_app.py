#!/usr/bin/env python3
"""
Simple startup script for TOR Analysis System
This version runs without Celery for easier setup
"""

import sys
import os
import subprocess
import time

def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print(f"❌ Redis not available: {e}")
        print("💡 You can still run the app without Redis (some features will be limited)")
        return False

def install_requirements():
    """Install minimal requirements"""
    packages = [
        'fastapi',
        'uvicorn',
        'jinja2',
        'python-multipart',
        'pydantic',
        'requests',
        'aiohttp',
        'python-dotenv'
    ]
    
    print("📦 Installing minimal requirements...")
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - already installed")
        except ImportError:
            print(f"📥 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def run_app():
    """Run the application"""
    print("\n🚀 Starting TOR Analysis System...")
    print("📍 Dashboard: http://localhost:8000")
    print("🔑 Login: admin / admin123")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Set environment
    os.environ.setdefault('PYTHONPATH', '.')
    
    try:
        # Try to run the full app first
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--reload', 
            '--host', '0.0.0.0', 
            '--port', '8000'
        ])
    except Exception as e:
        print(f"❌ Error running full app: {e}")
        print("🔄 Trying simplified version...")
        
        # Fallback to simplified app
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main_simple:app', 
            '--reload', 
            '--host', '0.0.0.0', 
            '--port', '8000'
        ])

if __name__ == "__main__":
    try:
        print("🔧 TOR Analysis System Setup")
        print("="*40)
        
        # Check Redis (optional)
        check_redis()
        
        # Install requirements
        install_requirements()
        
        # Small delay
        time.sleep(1)
        
        # Run the app
        run_app()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down TOR Analysis System...")
        print("Thank you for using our system!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Alternative options:")
        print("1. Try: docker-compose up -d")
        print("2. Try: python app/main_simple.py")
        print("3. Try: uvicorn app.main_simple:app --reload")