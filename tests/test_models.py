"""
Unit tests for The Dojo models.
Following TDD principles - tests written before implementation.
"""
import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.person import Person
from models.fellow import Fellow
from models.staff import Staff
from models.room import Room
from models.office import Office
from models.living_space import LivingSpace
from models.dojo import Dojo


class TestPerson(unittest.TestCase):
    """Test the Person base class."""
    
    def test_person_creation_with_name(self):
        """Test that a person can be created with a name."""
        # This will fail initially as Person class doesn't exist yet
        person = Person("John Doe")
        self.assertEqual(person.name, "John Doe")
        self.assertIsNotNone(person.person_id)
        self.assertTrue(len(person.person_id) > 0)
    
    def test_person_has_unique_id(self):
        """Test that each person gets a unique ID."""
        person1 = Person("John Doe")
        person2 = Person("Jane Smith")
        self.assertNotEqual(person1.person_id, person2.person_id)
    
    def test_person_string_representation(self):
        """Test the string representation of a person."""
        person = Person("John Doe")
        self.assertIn("John Doe", str(person))


class TestFellow(unittest.TestCase):
    """Test the Fellow class."""
    
    def test_fellow_creation_default_accommodation(self):
        """Test fellow creation with default accommodation preference."""
        fellow = Fellow("Alice Johnson")
        self.assertEqual(fellow.name, "Alice Johnson")
        self.assertEqual(fellow.person_type, "FELLOW")
        self.assertFalse(fellow.wants_accommodation)
        self.assertIsNone(fellow.office_allocated)
        self.assertIsNone(fellow.living_space_allocated)
    
    def test_fellow_creation_wants_accommodation(self):
        """Test fellow creation wanting accommodation."""
        fellow = Fellow("Bob Wilson", wants_accommodation="Y")
        self.assertTrue(fellow.wants_accommodation)
    
    def test_fellow_creation_no_accommodation(self):
        """Test fellow creation not wanting accommodation."""
        fellow = Fellow("Carol Brown", wants_accommodation="N")
        self.assertFalse(fellow.wants_accommodation)


class TestStaff(unittest.TestCase):
    """Test the Staff class."""
    
    def test_staff_creation(self):
        """Test staff creation."""
        staff = Staff("David Lee")
        self.assertEqual(staff.name, "David Lee")
        self.assertEqual(staff.person_type, "STAFF")
        self.assertIsNone(staff.office_allocated)
    
    def test_staff_no_living_space_attribute(self):
        """Test that staff doesn't have living space allocation attribute."""
        staff = Staff("Emma Davis")
        self.assertFalse(hasattr(staff, 'living_space_allocated'))


class TestRoom(unittest.TestCase):
    """Test the Room base class functionality through Office class."""
    
    def test_room_creation(self):
        """Test room creation with name."""
        room = Office("Test Office")
        self.assertEqual(room.name, "Test Office")
        self.assertEqual(len(room.occupants), 0)
        self.assertIsInstance(room.occupants, list)
    
    def test_room_add_occupant(self):
        """Test adding occupant to room."""
        room = Office("Test Office")
        result = room.add_occupant("person_123")
        self.assertTrue(result)
        self.assertIn("person_123", room.occupants)
    
    def test_room_remove_occupant(self):
        """Test removing occupant from room."""
        room = Office("Test Office")
        room.add_occupant("person_123")
        result = room.remove_occupant("person_123")
        self.assertTrue(result)
        self.assertNotIn("person_123", room.occupants)
    
    def test_room_remove_nonexistent_occupant(self):
        """Test removing occupant that doesn't exist."""
        room = Office("Test Office")
        result = room.remove_occupant("person_123")
        self.assertFalse(result)


class TestOffice(unittest.TestCase):
    """Test the Office class."""
    
    def test_office_creation(self):
        """Test office creation."""
        office = Office("Blue Office")
        self.assertEqual(office.name, "Blue Office")
        self.assertEqual(office.room_type, "office")
        self.assertEqual(office.capacity, 6)
        self.assertEqual(len(office.occupants), 0)
    
    def test_office_capacity_limit(self):
        """Test office capacity limit."""
        office = Office("Blue Office")
        # Add 6 people (at capacity)
        for i in range(6):
            result = office.add_occupant(f"person_{i}")
            self.assertTrue(result)
        
        # Try to add 7th person (should fail)
        result = office.add_occupant("person_6")
        self.assertFalse(result)
    
    def test_office_is_full(self):
        """Test office is_full method."""
        office = Office("Blue Office")
        self.assertFalse(office.is_full())
        
        # Fill to capacity
        for i in range(6):
            office.add_occupant(f"person_{i}")
        
        self.assertTrue(office.is_full())
    
    def test_office_available_space(self):
        """Test office available_space method."""
        office = Office("Blue Office")
        self.assertEqual(office.available_space(), 6)
        
        office.add_occupant("person_1")
        self.assertEqual(office.available_space(), 5)


class TestLivingSpace(unittest.TestCase):
    """Test the LivingSpace class."""
    
    def test_living_space_creation(self):
        """Test living space creation."""
        living_space = LivingSpace("Red Living Space")
        self.assertEqual(living_space.name, "Red Living Space")
        self.assertEqual(living_space.room_type, "living_space")
        self.assertEqual(living_space.capacity, 4)
        self.assertEqual(len(living_space.occupants), 0)
    
    def test_living_space_capacity_limit(self):
        """Test living space capacity limit."""
        living_space = LivingSpace("Red Living Space")
        # Add 4 people (at capacity)
        for i in range(4):
            result = living_space.add_occupant(f"person_{i}")
            self.assertTrue(result)
        
        # Try to add 5th person (should fail)
        result = living_space.add_occupant("person_4")
        self.assertFalse(result)
    
    def test_living_space_is_full(self):
        """Test living space is_full method."""
        living_space = LivingSpace("Red Living Space")
        self.assertFalse(living_space.is_full())
        
        # Fill to capacity
        for i in range(4):
            living_space.add_occupant(f"person_{i}")
        
        self.assertTrue(living_space.is_full())


class TestDojo(unittest.TestCase):
    """Test the Dojo main controller class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.dojo = Dojo()
    
    def test_dojo_creation(self):
        """Test dojo creation with empty collections."""
        self.assertEqual(len(self.dojo.offices), 0)
        self.assertEqual(len(self.dojo.living_spaces), 0)
        self.assertEqual(len(self.dojo.fellows), 0)
        self.assertEqual(len(self.dojo.staff), 0)
        self.assertEqual(len(self.dojo.people), 0)
    
    def test_create_office_successfully(self):
        """Test creating an office successfully."""
        initial_room_count = len(self.dojo.offices)
        result = self.dojo.create_room("office", "Blue Office")
        self.assertTrue(result)
        new_room_count = len(self.dojo.offices)
        self.assertEqual(new_room_count - initial_room_count, 1)
        self.assertEqual(self.dojo.offices[0].name, "Blue Office")
    
    def test_create_living_space_successfully(self):
        """Test creating a living space successfully."""
        initial_room_count = len(self.dojo.living_spaces)
        result = self.dojo.create_room("living_space", "Red Living Space")
        self.assertTrue(result)
        new_room_count = len(self.dojo.living_spaces)
        self.assertEqual(new_room_count - initial_room_count, 1)
        self.assertEqual(self.dojo.living_spaces[0].name, "Red Living Space")
    
    def test_create_room_invalid_type(self):
        """Test creating room with invalid type."""
        result = self.dojo.create_room("invalid_type", "Test Room")
        self.assertFalse(result)
    
    def test_add_staff_successfully(self):
        """Test adding staff successfully."""
        # First create an office
        self.dojo.create_room("office", "Blue Office")
        
        initial_staff_count = len(self.dojo.staff)
        result = self.dojo.add_person("John Doe", "STAFF")
        self.assertTrue(result)
        new_staff_count = len(self.dojo.staff)
        self.assertEqual(new_staff_count - initial_staff_count, 1)
        
        # Check staff was allocated to office
        staff_member = self.dojo.staff[0]
        self.assertEqual(staff_member.name, "John Doe")
        self.assertIsNotNone(staff_member.office_allocated)
    
    def test_add_fellow_without_accommodation(self):
        """Test adding fellow without accommodation."""
        # First create an office
        self.dojo.create_room("office", "Blue Office")
        
        initial_fellow_count = len(self.dojo.fellows)
        result = self.dojo.add_person("Jane Smith", "FELLOW", "N")
        self.assertTrue(result)
        new_fellow_count = len(self.dojo.fellows)
        self.assertEqual(new_fellow_count - initial_fellow_count, 1)
        
        # Check fellow was allocated to office but not living space
        fellow = self.dojo.fellows[0]
        self.assertEqual(fellow.name, "Jane Smith")
        self.assertIsNotNone(fellow.office_allocated)
        self.assertIsNone(fellow.living_space_allocated)
    
    def test_add_fellow_with_accommodation(self):
        """Test adding fellow with accommodation."""
        # First create an office and living space
        self.dojo.create_room("office", "Blue Office")
        self.dojo.create_room("living_space", "Red Living Space")
        
        result = self.dojo.add_person("Bob Wilson", "FELLOW", "Y")
        self.assertTrue(result)
        
        # Check fellow was allocated to both office and living space
        fellow = self.dojo.fellows[0]
        self.assertEqual(fellow.name, "Bob Wilson")
        self.assertIsNotNone(fellow.office_allocated)
        self.assertIsNotNone(fellow.living_space_allocated)
    
    def test_add_person_no_available_office(self):
        """Test adding person when no office is available."""
        result = self.dojo.add_person("John Doe", "STAFF")
        # Should still create the person but not allocate office
        self.assertTrue(result)
        self.assertEqual(len(self.dojo.staff), 1)
        self.assertIsNone(self.dojo.staff[0].office_allocated)


if __name__ == '__main__':
    unittest.main()
