"""
SCIM 2.0 Endpoints Application Runner

This script initializes the database and starts the SCIM endpoints server.
"""

import logging
import uvicorn

from .init_db import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_server() -> None:
    """Initialize database and run the server."""
    logger.info("Starting SCIM 2.0 Endpoints server...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Run HTTP server
        logger.info("Starting server on HTTP port 8000...")
        logger.info("Access the API at: http://localhost:8000")
        logger.info("API Documentation: http://localhost:8000/docs")
        
        uvicorn.run(
            "src.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
            
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise


if __name__ == "__main__":
    run_server()
