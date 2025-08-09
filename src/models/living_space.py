"""
LivingSpace class for The Dojo application.
"""
from .room import Room


class LivingSpace(Room):
    """LivingSpace class - a type of room with a capacity of 4 people."""
    
    def __init__(self, name):
        """
        Initialize a LivingSpace.
        
        Args:
            name (str): The living space's name
        """
        super().__init__(name)
        self.room_type = "living_space"
        self.capacity = 4  # Living spaces can accommodate 4 people
