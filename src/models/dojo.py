"""
Dojo class for The Dojo application.
"""
import random
from .person import Person
from .fellow import Fellow
from .staff import Staff
from .office import Office
from .living_space import LivingSpace


class Dojo:
    """Main class that manages the entire Dojo space allocation system."""
    
    def __init__(self):
        """Initialize a new Dojo with empty lists for rooms and people."""
        self.offices = []  # List of Office objects
        self.living_spaces = []  # List of LivingSpace objects
        self.people = []  # List of all Person objects
        self.staff = []  # List of Staff objects
        self.fellows = []  # List of Fellow objects
    
    def _add_person_to_lists(self, person):
        """
        Add a person to the appropriate lists.
        
        Args:
            person (Person): The person object to add
        """
        self.people.append(person)
        if person.person_type == 'FELLOW':
            self.fellows.append(person)
        else:  # STAFF
            self.staff.append(person)
        
    def create_room(self, room_type, room_names):
        """
        Create one or more rooms of the specified type.
        
        Args:
            room_type (str): Type of room ('office' or 'living_space')
            room_names (str or list): Single room name or list of room names to create
            
        Returns:
            bool: True if any rooms were created, False otherwise
        """
        if room_type not in ['office', 'living_space']:
            return False
            
        # Convert single string to list for consistent processing
        if isinstance(room_names, str):
            room_names = [room_names]
        elif not isinstance(room_names, (list, tuple)):
            return False
            
        rooms_created = False
        for name in room_names:
            # Skip empty names
            if not name or not isinstance(name, str) or not name.strip():
                continue
                
            # Skip if room name already exists
            if any(room.name.lower() == name.lower() 
                  for room in (self.offices + self.living_spaces)):
                continue
                
            if room_type == 'office':
                room = Office(name)
                self.offices.append(room)
            else:  # living_space
                room = LivingSpace(name)
                self.living_spaces.append(room)
            
            rooms_created = True
            # Format the output message with correct article
            room_type_display = 'living space' if room_type == 'living_space' else room_type
            article = 'An' if room_type_display[0].lower() in 'aeiou' else 'A'
            print(f"{article} {room_type_display} called {name} has been successfully created!")
            
        return rooms_created
    
    def add_person(self, name, person_type, wants_accommodation="N"):
        """
        Add a new person to the Dojo and allocate them a random room.
        
        Args:
            name (str): Person's name
            person_type (str): Type of person ('FELLOW' or 'STAFF')
            wants_accommodation (str): 'Y' if they want accommodation, 'N' otherwise
            
        Returns:
            bool: True if person was added successfully, False otherwise
        """
        # Validate person type
        person_type = person_type.upper()
        if person_type not in ['FELLOW', 'STAFF']:
            return False
            
        # Create the appropriate person object
        try:
            if person_type == 'FELLOW':
                person = Fellow(name, wants_accommodation)
            else:  # STAFF
                if isinstance(wants_accommodation, str) and wants_accommodation.upper() == 'Y':
                    return False  # Staff cannot have accommodation
                person = Staff(name)
                
            # Store the person in appropriate lists
            self._add_person_to_lists(person)
            
            # Allocate office space
            office = self._allocate_office(person)
            first_name = name.split()[0]  # Get first name for output
            office_msg = f"{first_name} has been allocated the office {office.name}" if office else "No office available"
            
            # Allocate living space if fellow wants it
            living_msg = ""
            if person_type == 'FELLOW' and person.wants_accommodation:
                living_space = self._allocate_living_space(person)
                living_msg = f"\n{first_name} has been allocated the livingspace {living_space.name}" if living_space else "\nNo living space available"
            
            # Format the output to match test expectations
            person_type_str = "Fellow" if person_type == 'FELLOW' else "Staff"
            print(f"{person_type_str} {name} has been successfully added.\n{office_msg}{living_msg}")
            return True
            
        except Exception as e:
            print(f"Error adding person: {e}", file=sys.stderr)
            return False
        return True
    
    def _allocate_office(self, person):
        """
        Allocate an office to a person.
        
        Args:
            person: Person object to allocate office to
            
        Returns:
            Office: The allocated office or None if none available
        """
        # Try to find an office with space
        available_offices = [o for o in self.offices if not o.is_full()]
        if not available_offices:
            return None
            
        # Randomly select an office
        office = random.choice(available_offices)
        office.add_occupant(person.person_id)
        person.office_allocated = office.name
        return office
    
    def _allocate_living_space(self, fellow):
        """
        Allocate a living space to a fellow.
        
        Args:
            fellow: Fellow object to allocate living space to
            
        Returns:
            LivingSpace: The allocated living space or None if none available
        """
        # Try to find a living space with space
        available_spaces = [ls for ls in self.living_spaces if not ls.is_full()]
        if not available_spaces:
            return None
            
        # Randomly select a living space
        living_space = random.choice(available_spaces)
        living_space.add_occupant(fellow.person_id)
        fellow.living_space_allocated = living_space.name
        return living_space
