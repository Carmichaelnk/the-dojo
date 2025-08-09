"""
Database models for Room, Office, and LivingSpace.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import Base
from .person_models import PersonDB

class RoomDB(Base):
    """Base database model for rooms in The Dojo."""
    __tablename__ = 'rooms'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'office' or 'living_space'
    capacity = Column(Integer, nullable=False)
    
    # Relationships
    office_occupants = relationship("PersonDB", 
                                  foreign_keys="[PersonDB.office_id]")
    living_space_occupants = relationship("PersonDB", 
                                        foreign_keys="[PersonDB.living_space_id]")
    
    # For many-to-many relationship (if needed)
    occupants = relationship("PersonDB",
                           secondary='person_room_association',
                           back_populates="rooms")
    
    def __init__(self, room_id, name, room_type, capacity):
        """Initialize a room.
        
        Args:
            room_id (str): The room's unique ID
            name (str): The room's name
            room_type (str): 'office' or 'living_space'
            capacity (int): Maximum number of occupants
        """
        self.id = room_id
        self.name = name
        self.type = room_type.lower()
        self.capacity = capacity
    
    def __repr__(self):
        return f"<{self.type.capitalize()} {self.name} (Capacity: {self.capacity})>"


class OfficeDB(RoomDB):
    """Database model for an office room."""
    __tablename__ = 'offices'
    
    id = Column(String, ForeignKey('rooms.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'office'
    }
    
    def __init__(self, room_id, name):
        """Initialize an office.
        
        Args:
            room_id (str): The office's unique ID
            name (str): The office's name
        """
        super().__init__(room_id, name, 'office', 6)  # Office capacity is 6


class LivingSpaceDB(RoomDB):
    """Database model for a living space."""
    __tablename__ = 'living_spaces'
    
    id = Column(String, ForeignKey('rooms.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'living_space'
    }
    
    def __init__(self, room_id, name):
        """Initialize a living space.
        
        Args:
            room_id (str): The living space's unique ID
            name (str): The living space's name
        """
        super().__init__(room_id, name, 'living_space', 4)  # Living space capacity is 4
