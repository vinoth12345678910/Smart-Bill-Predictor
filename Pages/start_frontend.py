#!/usr/bin/env python3
"""
Frontend Startup Script
Runs the Next.js development server with proper configuration
"""

import subprocess
import os
import sys

def main():
    frontend_dir = "Smart-bill-frontend"
    
    # Check if frontend directory exists
    if not os.path.exists(frontend_dir):
        print(f"❌ Frontend directory '{frontend_dir}' not found!")
        print("Please make sure you're in the correct directory.")
        sys.exit(1)
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    print(f"🚀 Starting Smart Bill Frontend...")
    print(f"📍 Frontend will be available at: http://localhost:3000")
    print(f"🔗 Backend API: http://localhost:8000")
    
    try:
        # Check if node_modules exists, if not install dependencies
        if not os.path.exists("node_modules"):
            print("📦 Installing dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Start the development server
        print("🌐 Starting Next.js development server...")
        subprocess.run(["npm", "run", "dev"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
