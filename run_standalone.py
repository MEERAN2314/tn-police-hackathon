#!/usr/bin/env python3
"""
Run the standalone TOR Analysis System
This version has zero external dependencies except FastAPI
"""

import subprocess
import sys
import os

def install_requirements():
    """Install minimal requirements"""
    required = ['fastapi', 'uvicorn', 'python-multipart']
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def main():
    print("🚀 TOR Analysis System - Standalone Version")
    print("=" * 50)
    
    # Install requirements
    install_requirements()
    
    print("\n🌟 Starting application...")
    print("📍 URL: http://localhost:8001")
    print("🔑 Login: admin / admin123")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    # Run the app
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'simple_app:app', 
            '--reload', 
            '--host', '0.0.0.0', 
            '--port', '8001'
        ])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Try running manually:")
        print("python -m uvicorn simple_app:app --reload --port 8001")

if __name__ == "__main__":
    main()