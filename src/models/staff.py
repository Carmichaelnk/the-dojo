"""
Staff class for The Dojo application.
"""
from .person import Person


class Staff(Person):
    """Staff class - can be allocated office."""
    
    def __init__(self, name):
        """
        Initialize a Staff.
        
        Args:
            name (str): The staff's name
        """
        super().__init__(name)
        self.person_type = "STAFF"
        self.office_allocated = None
