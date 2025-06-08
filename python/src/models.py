"""
Database models for SCIM 2.0 endpoints using SQLAlchemy.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime, 
    ForeignKey, create_engine, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from typing import Optional
import uuid
import json

Base = declarative_base()


class Realm(Base):
    """Table to store realm information for SCIM endpoints."""
    __tablename__ = 'realms'
    
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    realm_id: str = Column(String(50), unique=True, nullable=False, index=True)
    name: str = Column(String(100), nullable=False)
    description: Optional[str] = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    scim_users = relationship("SCIMUser", back_populates="realm", cascade="all, delete-orphan")
    scim_idps = relationship("SCIMIDP", back_populates="realm", cascade="all, delete-orphan")


class SCIMUser(Base):
    """SCIM User table following SCIM 2.0 core schema."""
    __tablename__ = 'scim_users'
    
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: str = Column(String(50), unique=True, nullable=False, index=True)
    realm_id: str = Column(String(50), ForeignKey('realms.realm_id'), nullable=False)
    
    # SCIM Core Schema fields
    schemas: str = Column(Text, nullable=False)  # JSON string
    userName: str = Column(String(100), nullable=False, index=True)
    externalId: Optional[str] = Column(String(100), index=True)
    firstName: str = Column(String(100), nullable=False)
    surName: str = Column(String(100), nullable=False)
    displayName: str = Column(String(200), nullable=False)
    active: bool = Column(Boolean, default=True, nullable=False)
    emails: str = Column(Text, nullable=False)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    realm = relationship("Realm", back_populates="scim_users")
    
    # Composite indexes for better performance
    __table_args__ = (
        Index('idx_realm_username', 'realm_id', 'userName'),
        Index('idx_realm_external', 'realm_id', 'externalId'),
    )


class SCIMIDP(Base):
    """SCIM IDP table for identity provider users."""
    __tablename__ = 'scim_idp'
    
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: str = Column(String(50), unique=True, nullable=False, index=True)
    realm_id: str = Column(String(50), ForeignKey('realms.realm_id'), nullable=False)
    
    # SCIM Core Schema fields
    schemas: str = Column(Text, nullable=False)  # JSON string
    userName: str = Column(String(100), nullable=False, index=True)
    externalId: Optional[str] = Column(String(100), index=True)
    firstName: str = Column(String(100), nullable=False)
    surName: str = Column(String(100), nullable=False)
    displayName: str = Column(String(200), nullable=False)
    active: bool = Column(Boolean, default=True, nullable=False)
    emails: str = Column(Text, nullable=False)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    realm = relationship("Realm", back_populates="scim_idps")
    
    # Composite indexes for better performance
    __table_args__ = (
        Index('idx_idp_realm_username', 'realm_id', 'userName'),
        Index('idx_idp_realm_external', 'realm_id', 'externalId'),
    )


class AdminUser(Base):
    """Authentication table for SCIM endpoint administrators."""
    __tablename__ = 'admin_users'
    
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(100), unique=True, nullable=False, index=True)
    password_hash: str = Column(String(255), nullable=False)
    email: str = Column(String(255), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)


def generate_unique_id() -> str:
    """Generate a unique ID for users."""
    return str(uuid.uuid4())


def generate_realm_id() -> str:
    """Generate a unique realm ID."""
    return f"realm_{uuid.uuid4().hex[:8]}"


# Database engine and session factory
engine = create_engine('sqlite:///scim_database.db', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Database dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
