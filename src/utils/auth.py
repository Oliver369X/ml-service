"""
Authentication utilities
Extract userId and permissions from headers sent by gateway
"""
from typing import Optional
from fastapi import Header, HTTPException, status


def get_user_id_from_headers(
    userid: Optional[str] = Header(None, alias="userid"),
    user_id: Optional[str] = Header(None, alias="user-id")
) -> str:
    """
    Extract user ID from headers
    
    The gateway sends userId in headers after validating JWT.
    We trust the gateway and don't re-validate JWT here.
    
    Args:
        userid: User ID from header (lowercase)
        user_id: User ID from header (with dash)
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If userId not found in headers
    """
    uid = userid or user_id
    
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in headers. Request must come through gateway."
        )
    
    return uid


def get_permissions_from_headers(
    permissions: Optional[str] = Header(None)
) -> list[str]:
    """
    Extract permissions from headers
    
    Args:
        permissions: Comma-separated permissions string
        
    Returns:
        List of permission strings
    """
    if not permissions:
        return []
    
    return [p.strip() for p in permissions.split(',')]

