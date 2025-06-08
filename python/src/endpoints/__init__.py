"""
SCIM 2.0 Endpoints Module

This module contains the endpoint definitions for SCIM 2.0 user management.
"""

from .scim_endpoints import router as scim_router

__all__ = ["scim_router"]