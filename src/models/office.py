"""
Office class for The Dojo application.
"""
from .room import Room


class Office(Room):
    """Office class - a type of room with a capacity of 6 people."""
    
    def __init__(self, name):
        """
        Initialize an Office.
        
        Args:
            name (str): The office's name
        """
        super().__init__(name)
        self.room_type = "office"
        self.capacity = 6  # Offices can accommodate 6 people
