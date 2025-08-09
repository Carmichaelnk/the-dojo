"""
Person base class for The Dojo application.
"""
import uuid
from abc import ABC


class Person(ABC):
    """Abstract base class for all people in The Dojo."""
    
    def __init__(self, name):
        """
        Initialize a Person with a name and unique ID.
        
        Args:
            name (str): The person's name
        """
        self.name = name
        self.person_id = str(uuid.uuid4())[:8]  # Short unique ID
        self.person_type = None  # Will be set by subclasses
    
    def __str__(self):
        """Return string representation of the person."""
        return f"{self.person_type}: {self.name} (ID: {self.person_id})"
