"""
Database models for Person, Fellow, and Staff.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship

from .base import Base

# Association table for many-to-many relationship between people and rooms
person_room_association = Table(
    'person_room_association',
    Base.metadata,
    Column('person_id', String, ForeignKey('people.id')),
    Column('room_id', String, ForeignKey('rooms.id'))
)

class PersonDB(Base):
    """Database model for a person in The Dojo."""
    __tablename__ = 'people'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'FELLOW' or 'STAFF'
    
    # Relationships
    office_id = Column(String, ForeignKey('rooms.id'), nullable=True)
    living_space_id = Column(String, ForeignKey('rooms.id'), nullable=True)
    
    # Backrefs
    office = relationship("RoomDB", foreign_keys=[office_id], back_populates="office_occupants")
    living_space = relationship("RoomDB", foreign_keys=[living_space_id], back_populates="living_space_occupants")
    
    # For many-to-many relationship (if needed)
    rooms = relationship("RoomDB", 
                        secondary=person_room_association,
                        back_populates="occupants")
    
    def __init__(self, person_id, name, person_type):
        """Initialize a person.
        
        Args:
            person_id (str): The person's unique ID
            name (str): The person's name
            person_type (str): 'FELLOW' or 'STAFF'
        """
        self.id = person_id
        self.name = name
        self.type = person_type.upper()
    
    def __repr__(self):
        return f"<{self.type} {self.name} (ID: {self.id})>"


class StaffDB(PersonDB):
    """Database model for a staff member."""
    __mapper_args__ = {
        'polymorphic_identity': 'STAFF'
    }
    
    def __init__(self, person_id, name):
        """Initialize a staff member.
        
        Args:
            person_id (str): The staff's unique ID
            name (str): The staff's name
        """
        super().__init__(person_id, name, 'STAFF')


class FellowDB(PersonDB):
    """Database model for a fellow."""
    __tablename__ = 'fellows'
    
    id = Column(String, ForeignKey('people.id'), primary_key=True)
    wants_accommodation = Column(Boolean, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'FELLOW'
    }
    
    def __init__(self, person_id, name, wants_accommodation=False):
        """Initialize a fellow.
        
        Args:
            person_id (str): The fellow's unique ID
            name (str): The fellow's name
            wants_accommodation (bool): Whether the fellow wants accommodation
        """
        super().__init__(person_id, name, 'FELLOW')
        self.wants_accommodation = bool(wants_accommodation)
