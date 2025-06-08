"""
Database initialization script for SCIM 2.0 endpoints.
Creates all necessary tables and initial data.
"""

import logging
from sqlalchemy.orm import Session

from .models import create_tables, SessionLocal, generate_realm_id
from .database_service import DatabaseService
from .schemas import RealmCreate, AdminUserCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database() -> None:
    """Initialize the database with tables and default data."""
    logger.info("Initializing SCIM database...")
    
    # Create all tables
    create_tables()
    logger.info("Database tables created successfully")
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Create default realms for scim_user and scim_idp tables
        realms_to_create = [
            {"name": "SCIM Users Realm", "description": "Default realm for SCIM user provisioning"},
            {"name": "SCIM IDP Realm", "description": "Default realm for SCIM IDP user provisioning"}
        ]
        
        for realm_data in realms_to_create:
            # Check if realm already exists
            existing_realms = DatabaseService.get_all_realms(db)
            if not any(realm.name == realm_data["name"] for realm in existing_realms):
                realm_create = RealmCreate(**realm_data)
                realm = DatabaseService.create_realm(db, realm_create)
                logger.info(f"Created realm: {realm.name} with ID: {realm.realm_id}")
            else:
                logger.info(f"Realm '{realm_data['name']}' already exists, skipping creation")
          # Create default admin user if not exists
        admin_username = "admin"
        existing_admin = DatabaseService.get_admin_user(db, admin_username)
        
        if not existing_admin:
            admin_create = AdminUserCreate(
                username=admin_username,
                password="admin123",  # Change this in production!
                email="admin@example.com"
            )
            admin_user = DatabaseService.create_admin_user(db, admin_create)
            logger.info(f"Created default admin user: {admin_user.username}")
            logger.warning("Default admin password is 'admin123' - Change this in production!")
        else:
            logger.info("Default admin user already exists, skipping creation")
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
    
    logger.info("Database initialization completed successfully")


if __name__ == "__main__":
    init_database()