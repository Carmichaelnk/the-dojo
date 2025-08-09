"""
Fellow class for The Dojo application.
"""
from .person import Person


class Fellow(Person):
    """Fellow class - can be allocated office and living space."""
    
    def __init__(self, name, wants_accommodation="N"):
        """
        Initialize a Fellow.
        
        Args:
            name (str): The fellow's name
            wants_accommodation (str or bool): "Y"/True if wants accommodation, "N"/False otherwise
        """
        super().__init__(name)
        self.person_type = "FELLOW"
        if isinstance(wants_accommodation, str):
            self.wants_accommodation = wants_accommodation.upper() == "Y"
        else:
            self.wants_accommodation = bool(wants_accommodation)
        self.office_allocated = None
        self.living_space_allocated = None
