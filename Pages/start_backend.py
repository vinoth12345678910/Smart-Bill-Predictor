#!/usr/bin/env python3
"""
Backend Startup Script
Runs the FastAPI server with proper configuration for frontend integration
"""

import uvicorn
import os
import sys

def main():
    # Set default port
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    
    print(f"🚀 Starting Smart Bill Coach Backend...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )

if __name__ == "__main__":
    main()
