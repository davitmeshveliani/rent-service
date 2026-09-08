"""
Models module for the Users application.
Exposes domain model classes for clean package-level imports.
"""

from .user import User

__all__: list[str] = [
    "User",
]