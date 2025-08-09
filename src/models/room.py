"""
Room base class for The Dojo application.
"""
from abc import ABC, abstractmethod


class Room(ABC):
    """Abstract base class for all rooms in The Dojo."""
    
    def __init__(self, name):
        """
        Initialize a Room with a name.
        
        Args:
            name (str): The room's name
        """
        if self.__class__ == Room:
            raise TypeError("Cannot instantiate abstract class Room directly")
            
        self.name = name
        self.room_type = None  # Will be set by subclasses
        self.capacity = 0  # Will be set by subclasses
        self.occupants = []  # List of person IDs
    
    def add_occupant(self, person_id):
        """
        Add an occupant to the room if there's space.
        
        Args:
            person_id (str): The person's unique ID
            
        Returns:
            bool: True if successfully added or already in room, False if room is full
        """
        if not person_id:
            return False
            
        if person_id in self.occupants:
            return True  # Already in the room
            
        if self.is_full():
            return False
            
        self.occupants.append(person_id)
        return True
    
    def remove_occupant(self, person_id):
        """
        Remove an occupant from the room.
        
        Args:
            person_id (str): The person's unique ID
            
        Returns:
            bool: True if successfully removed, False if person not found or invalid ID
        """
        if not person_id or not self.occupants:
            return False
            
        try:
            self.occupants.remove(person_id)
            return True
        except ValueError:
            return False
    
    def is_full(self):
        """
        Check if the room is at capacity.
        
        Returns:
            bool: True if room is full, False otherwise
        """
        return len(self.occupants) >= self.capacity
    
    def available_space(self):
        """
        Get the number of available spaces in the room.
        
        Returns:
            int: Number of available spaces
        """
        return self.capacity - len(self.occupants)
    
    def __str__(self):
        """Return string representation of the room."""
        return f"{self.room_type}: {self.name} ({len(self.occupants)}/{self.capacity})"
    