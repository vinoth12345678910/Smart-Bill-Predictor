#!/usr/bin/env python3
"""
Full Stack Startup Script
Runs both frontend and backend servers simultaneously
"""

import subprocess
import threading
import time
import os
import sys
import signal

def run_backend():
    """Run the backend server"""
    try:
        print("🚀 Starting Backend Server...")
        subprocess.run([sys.executable, "start_backend.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend error: {e}")
    except KeyboardInterrupt:
        print("👋 Backend stopped by user")

def run_frontend():
    """Run the frontend server"""
    try:
        print("🌐 Starting Frontend Server...")
        subprocess.run([sys.executable, "start_frontend.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend error: {e}")
    except KeyboardInterrupt:
        print("👋 Frontend stopped by user")

def main():
    print("🎯 Smart Bill Coach - Full Stack Startup")
    print("=" * 50)
    print("📍 Backend API: http://localhost:8000")
    print("🌐 Frontend App: http://localhost:3000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend in main thread
    run_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Full stack application stopped by user")
        sys.exit(0)
