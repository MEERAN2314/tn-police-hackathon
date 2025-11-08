#!/usr/bin/env python3
"""
Run TOR Analysis System with automatic port detection
"""

import subprocess
import sys
import socket

def find_free_port(start_port=8000, max_port=8010):
    """Find a free port starting from start_port"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

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
    print("🚀 TOR Analysis System - Auto Port Detection")
    print("=" * 50)
    
    # Install requirements
    install_requirements()
    
    # Find available port
    port = find_free_port()
    if not port:
        print("❌ No available ports found between 8000-8010")
        print("💡 Try stopping other applications or use a different port range")
        return
    
    print(f"\n🌟 Starting application on port {port}...")
    print(f"📍 URL: http://localhost:{port}")
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
            '--port', str(port)
        ])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Try running manually:")
        print(f"python -m uvicorn simple_app:app --reload --port {port}")

if __name__ == "__main__":
    main()