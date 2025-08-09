"""
Utility functions for database operations.
"""
import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from .base import Base, Database
from .person_models import PersonDB, StaffDB, FellowDB
from .room_models import RoomDB, OfficeDB, LivingSpaceDB
from src.models.person import Person
from src.models.staff import Staff
from src.models.fellow import Fellow
from src.models.room import Room
from src.models.office import Office
from src.models.living_space import LivingSpace
from src.models.dojo import Dojo

def init_db(db_url=None):
    """Initialize the database and create tables if they don't exist.
    
    Args:
        db_url (str, optional): Database URL. If None, uses SQLite in-memory.
        
    Returns:
        Database: Database instance
    """
    if db_url is None:
        db_url = 'sqlite:///:memory:'
    
    # Ensure directory exists for SQLite file
    if db_url.startswith('sqlite:///') and db_url != 'sqlite:///:memory:':
        db_path = db_url[10:]  # Remove 'sqlite:///'
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    db = Database(db_url)
    Base.metadata.create_all(db.engine)
    return db

def to_db_person(person):
    """Convert a domain Person to a database Person.
    
    Args:
        person (Person): Domain model person
        
    Returns:
        PersonDB: Database model person
    """
    # Check person_type first since isinstance() might not work due to import issues
    if hasattr(person, 'person_type'):
        if person.person_type == 'STAFF':
            # Create a StaffDB which will handle the PersonDB creation
            db_person = StaffDB(
                person_id=person.person_id,
                name=person.name
            )
        elif person.person_type == 'FELLOW':
            # Create a FellowDB which will handle the PersonDB creation
            db_person = FellowDB(
                person_id=person.person_id,
                name=person.name,
                wants_accommodation=getattr(person, 'wants_accommodation', False)
            )
        else:
            raise ValueError(f"Unknown person type: {person.person_type}")
    else:
        # Fallback to isinstance if person_type is not available
        try:
            if isinstance(person, Staff):
                db_person = StaffDB(
                    person_id=person.person_id,
                    name=person.name
                )
            elif isinstance(person, Fellow):
                db_person = FellowDB(
                    person_id=person.person_id,
                    name=person.name,
                    wants_accommodation=getattr(person, 'wants_accommodation', False)
                )
            else:
                raise ValueError(f"Unknown person type: {type(person)}")
        except (NameError, ImportError):
            raise ValueError(f"Cannot determine person type for {person}. Missing person_type attribute.")
    
    # Set room assignments if they exist
    if hasattr(person, 'office_allocated') and person.office_allocated:
        db_person.office_id = person.office_allocated
    
    if hasattr(person, 'living_space_allocated') and person.living_space_allocated:
        db_person.living_space_id = person.living_space_allocated
    
    return db_person

def to_domain_person(db_person, dojo):
    """Convert a database Person to a domain Person.
    
    Args:
        db_person (PersonDB): Database model person
        dojo (Dojo): Dojo instance to add the person to
        
    Returns:
        Person: Domain model person
    """
    # Check if this is a FellowDB instance (which has wants_accommodation)
    if hasattr(db_person, '__table__') and db_person.__table__.name == 'fellows':
        # It's a FellowDB instance, so we can access wants_accommodation
        person = Fellow(db_person.name, wants_accommodation=db_person.wants_accommodation)
    elif db_person.type == 'STAFF':
        person = Staff(db_person.name)
    else:  # FELLOW but not a FellowDB instance (shouldn't happen, but handle it)
        person = Fellow(db_person.name, wants_accommodation=False)
    
    # Set the person ID to match the database
    person.person_id = db_person.id
    
    # Add to dojo's people list
    dojo.people.append(person)
    
    # Set room assignments if they exist
    if db_person.office_id:
        person.office_allocated = db_person.office_id
    
    if db_person.living_space_id:
        person.living_space_allocated = db_person.living_space_id
    
    return person

def to_db_room(room):
    """Convert a domain Room to a database Room.
    
    Args:
        room (Room): Domain model room
        
    Returns:
        RoomDB: Database model room
    """
    # Get the class name as a string to handle potential import/class reference issues
    room_class_name = room.__class__.__name__
    
    # Use the room's name as the ID since that's the unique identifier in the domain model
    room_id = room.name.lower().replace(' ', '_')  # Create a simple ID from the name
    
    if room_class_name == 'Office' or (hasattr(room, 'room_type') and room.room_type == 'office'):
        db_room = OfficeDB(
            room_id=room_id,
            name=room.name
        )
    elif room_class_name == 'LivingSpace' or (hasattr(room, 'room_type') and room.room_type == 'living_space'):
        db_room = LivingSpaceDB(
            room_id=room_id,
            name=room.name
        )
    else:
        # Try to determine room type from the room's class name or attributes
        if hasattr(room, 'capacity'):
            if room.capacity == 6:  # Office capacity
                db_room = OfficeDB(room_id=room_id, name=room.name)
            elif room.capacity == 4:  # Living space capacity
                db_room = LivingSpaceDB(room_id=room_id, name=room.name)
            else:
                raise ValueError(f"Unknown room type with capacity={room.capacity}")
        else:
            raise ValueError(f"Unknown room type: {type(room)}. Class name: {room_class_name}, Attributes: {vars(room)}")
    
    return db_room

def to_domain_room(db_room, dojo):
    """Convert a database Room to a domain Room.
    
    Args:
        db_room (RoomDB): Database model room
        dojo (Dojo): Dojo instance to add the room to
        
    Returns:
        Room: Domain model room
    """
    # First, check if a room with this name already exists in the dojo
    existing_room = None
    room_name = db_room.name
    
    # Check in offices
    for office in dojo.offices:
        if office.name == room_name:
            existing_room = office
            break
    
    # If not found in offices, check in living spaces
    if existing_room is None:
        for living_space in dojo.living_spaces:
            if living_space.name == room_name:
                existing_room = living_space
                break
    
    # If room already exists, return it
    if existing_room is not None:
        return existing_room
    
    # Determine the room type from the database record
    room_type = getattr(db_room, 'type', None) or getattr(db_room, 'room_type', None)
    
    # Create a new room if it doesn't exist
    if room_type == 'office':
        room = Office(room_name)
        dojo.offices.append(room)
    elif room_type == 'living_space' or room_type == 'living space':
        room = LivingSpace(room_name)
        dojo.living_spaces.append(room)
    else:
        # Try to determine room type from capacity if type is not set
        if hasattr(db_room, 'capacity'):
            if db_room.capacity == 6:  # Office capacity
                room = Office(room_name)
                dojo.offices.append(room)
            elif db_room.capacity == 4:  # Living space capacity
                room = LivingSpace(room_name)
                dojo.living_spaces.append(room)
            else:
                raise ValueError(f"Unknown room type with capacity={db_room.capacity}")
        else:
            raise ValueError(f"Unknown room type: {room_type}")
    
    # Restore occupants if they exist in the database
    if hasattr(db_room, 'occupants'):
        for occupant_id in db_room.occupants:
            room.add_occupant(occupant_id)
    
    return room
