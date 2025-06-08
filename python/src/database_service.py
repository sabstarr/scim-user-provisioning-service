"""
Database operations service for SCIM 2.0 endpoints.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional, Dict, Any
from passlib.context import CryptContext
import json

from .models import SCIMUser, SCIMIDP, Realm, AdminUser, generate_unique_id, generate_realm_id
from .schemas import (
    SCIMUserCreate, SCIMUserUpdate, RealmCreate, AdminUserCreate
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DatabaseService:
    """Service class for database operations."""

    @staticmethod
    def create_realm(db: Session, realm_data: RealmCreate) -> Realm:
        """Create a new realm."""
        realm = Realm(
            realm_id=generate_realm_id(),
            name=realm_data.name,
            description=realm_data.description
        )
        db.add(realm)
        db.commit()
        db.refresh(realm)
        return realm

    @staticmethod
    def get_realm_by_id(db: Session, realm_id: str) -> Optional[Realm]:
        """Get realm by realm_id."""
        return db.query(Realm).filter(Realm.realm_id == realm_id).first()

    @staticmethod
    def get_all_realms(db: Session) -> List[Realm]:
        """Get all realms."""
        return db.query(Realm).all()

    @staticmethod
    def create_scim_user(db: Session, user_data: SCIMUserCreate, realm_id: str) -> SCIMUser:
        """Create a new SCIM user."""
        # Verify realm exists
        realm = DatabaseService.get_realm_by_id(db, realm_id)
        if not realm:
            raise ValueError(f"Realm {realm_id} not found")

        # Create user
        user = SCIMUser(
            user_id=generate_unique_id(),
            realm_id=realm_id,
            schemas=json.dumps(user_data.schemas),
            userName=user_data.userName,
            externalId=user_data.externalId,
            firstName=user_data.firstName,
            surName=user_data.surName,
            displayName=user_data.displayName,
            active=user_data.active,
            emails=json.dumps([email.model_dump() for email in user_data.emails])
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_scim_user_by_id(db: Session, user_id: str, realm_id: str) -> Optional[SCIMUser]:
        """Get SCIM user by user_id and realm_id."""
        return db.query(SCIMUser).filter(
            and_(SCIMUser.user_id == user_id, SCIMUser.realm_id == realm_id)
        ).first()

    @staticmethod
    def get_scim_user_by_username(db: Session, username: str, realm_id: str) -> Optional[SCIMUser]:
        """Get SCIM user by username and realm_id."""
        return db.query(SCIMUser).filter(
            and_(SCIMUser.userName == username, SCIMUser.realm_id == realm_id)
        ).first()

    @staticmethod
    def get_scim_user_by_email(db: Session, email: str, realm_id: str) -> Optional[SCIMUser]:
        """Get SCIM user by email and realm_id."""
        users = db.query(SCIMUser).filter(SCIMUser.realm_id == realm_id).all()
        for user in users:
            emails_data = json.loads(user.emails)
            for email_obj in emails_data:
                if email_obj.get('value') == email:
                    return user
        return None

    @staticmethod
    def get_scim_users(
        db: Session, 
        realm_id: str, 
        start_index: int = 1, 
        count: int = 100,
        filter_query: Optional[str] = None
    ) -> tuple[List[SCIMUser], int]:
        """Get SCIM users with pagination and filtering."""
        query = db.query(SCIMUser).filter(SCIMUser.realm_id == realm_id)
        
        # Apply filter if provided
        if filter_query:
            # Simple filter implementation - can be enhanced
            query = query.filter(
                or_(
                    SCIMUser.userName.contains(filter_query),
                    SCIMUser.displayName.contains(filter_query),
                    SCIMUser.firstName.contains(filter_query),
                    SCIMUser.surName.contains(filter_query)
                )
            )
        
        total_count = query.count()
        users = query.offset(start_index - 1).limit(count).all()
        return users, total_count

    @staticmethod
    def update_scim_user(
        db: Session, 
        user_id: str, 
        realm_id: str, 
        user_data: SCIMUserUpdate    ) -> Optional[SCIMUser]:
        """Update SCIM user."""
        user = DatabaseService.get_scim_user_by_id(db, user_id, realm_id)
        if not user:
            return None
        
        # Update fields if provided
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'emails' and value:
                # Handle emails - convert to JSON regardless of input type
                if isinstance(value, list) and len(value) > 0:
                    if isinstance(value[0], dict):
                        # Already dictionaries from API request
                        setattr(user, field, json.dumps(value))
                    else:
                        # Pydantic EmailSchema objects
                        setattr(user, field, json.dumps([email.model_dump() for email in value]))
                else:
                    setattr(user, field, json.dumps(value if value else []))
            elif field == 'schemas' and value:
                setattr(user, field, json.dumps(value))
            elif value is not None:
                setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_scim_user(db: Session, user_id: str, realm_id: str) -> bool:
        """Delete SCIM user."""
        user = DatabaseService.get_scim_user_by_id(db, user_id, realm_id)
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def create_scim_idp_user(db: Session, user_data: SCIMUserCreate, realm_id: str) -> SCIMIDP:
        """Create a new SCIM IDP user."""
        # Verify realm exists
        realm = DatabaseService.get_realm_by_id(db, realm_id)
        if not realm:
            raise ValueError(f"Realm {realm_id} not found")

        # Create IDP user
        user = SCIMIDP(
            user_id=generate_unique_id(),
            realm_id=realm_id,
            schemas=json.dumps(user_data.schemas),
            userName=user_data.userName,
            externalId=user_data.externalId,
            firstName=user_data.firstName,
            surName=user_data.surName,
            displayName=user_data.displayName,
            active=user_data.active,
            emails=json.dumps([email.model_dump() for email in user_data.emails])
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_admin_user(db: Session, admin_data: AdminUserCreate) -> AdminUser:
        """Create a new admin user."""
        hashed_password = pwd_context.hash(admin_data.password)
        admin = AdminUser(
            username=admin_data.username,
            password_hash=hashed_password,
            email=admin_data.email
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def get_admin_user(db: Session, username: str) -> Optional[AdminUser]:
        """Get admin user by username."""
        return db.query(AdminUser).filter(AdminUser.username == username).first()

    @staticmethod
    def verify_admin_password(password: str, hashed_password: str) -> bool:
        """Verify admin password."""
        return pwd_context.verify(password, hashed_password)

    @staticmethod
    def user_to_dict(user: SCIMUser) -> Dict[str, Any]:
        """Convert SCIMUser to dictionary for response."""
        return {
            "id": user.user_id,
            "schemas": json.loads(user.schemas),
            "userName": user.userName,
            "externalId": user.externalId,
            "firstName": user.firstName,
            "surName": user.surName,
            "displayName": user.displayName,
            "active": user.active,
            "emails": json.loads(user.emails),
            "meta": {
                "resourceType": "User",
                "created": user.created_at.isoformat() if user.created_at else None,
                "lastModified": user.updated_at.isoformat() if user.updated_at else None,
                "location": f"/scim/v2/Realms/{user.realm_id}/Users/{user.user_id}"
            }
        }
