"""
GraphQL Context
Provides database session and user information to resolvers
"""
from typing import Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from strawberry.fastapi import BaseContext


@dataclass
class Context(BaseContext):
    """GraphQL execution context"""
    db: Session
    user_id: Optional[str] = None
    permissions: Optional[list[str]] = None
    
    def __post_init__(self):
        """Ensure permissions is a list"""
        if self.permissions is None:
            self.permissions = []
        elif isinstance(self.permissions, str):
            self.permissions = [p.strip() for p in self.permissions.split(',')]

