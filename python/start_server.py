#!/usr/bin/env python3
"""
SCIM 2.0 Endpoints Application Startup Script

This script initializes the database and starts the SCIM endpoints server.
Run from the python directory: python start_server.py
"""

import logging
import uvicorn
import sys
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Now we can import from src
from src.init_db import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main server startup function."""
    logger.info("Starting SCIM 2.0 Endpoints Server...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Start the server
        logger.info("Starting FastAPI server...")
        logger.info("Server will be available at:")
        logger.info("  - HTTP: http://localhost:8000")
        logger.info("  - API Documentation: http://localhost:8000/docs")
        logger.info("Default admin credentials: admin/admin123")
        logger.info("Press Ctrl+C to stop the server")
        
        # Start HTTP server
        uvicorn.run(
            "src.app:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise


if __name__ == "__main__":
    main()
