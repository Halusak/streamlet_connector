"""
Standalone API server for Streamlet Connector.
Serves media data and video files without UI.

Usage:
    python run_api.py [--host HOST] [--port PORT]

Default: localhost:5000
"""

import sys
import os
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api import CustomAPI
from src.media_database import MediaDatabase

def main():
    parser = argparse.ArgumentParser(description='Streamlet Connector API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    
    args = parser.parse_args()
    
    # Initialize database
    database = MediaDatabase()
    
    # Create and run API
    api = CustomAPI(host=args.host, port=args.port, database=database)
    
    print(f"\n{'='*60}")
    print(f"Streamlet Connector API Server")
    print(f"{'='*60}")
    print(f"Database: {len(database.get_all_items())} items loaded")
    print(f"Server: http://{args.host}:{args.port}")
    print(f"Demo: http://{args.host}:{args.port}/demo")
    print(f"{'='*60}\n")
    print("💡 Otevřete v prohlížeči pro web demo!")
    print(f"   http://localhost:{args.port}\n")
    
    try:
        api.run()
    except KeyboardInterrupt:
        print("\n\nShutting down API server...")
        sys.exit(0)

if __name__ == '__main__':
    main()
