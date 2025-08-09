"""
Database service for saving and loading Dojo state.
"""
import os
import sys
import sqlite3
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from .base import Database, Base
from .person_models import PersonDB, StaffDB, FellowDB
from .room_models import RoomDB, OfficeDB, LivingSpaceDB
from .utils import init_db, to_db_person, to_db_room, to_domain_person, to_domain_room
from src.models.dojo import Dojo
from src.models.person import Person
from src.models.staff import Staff
from src.models.fellow import Fellow
from src.models.room import Room
from src.models.office import Office
from src.models.living_space import LivingSpace

class DatabaseService:
    """Service for database operations."""
    
    # Default database path (can be overridden)
    DEFAULT_DB_PATH = os.path.join(os.path.expanduser('~'), '.dojo', 'dojo.db')
    
    def __init__(self, db_url=None):
        """Initialize the database service.
        
        Args:
            db_url (str, optional): Database URL. If None, uses default SQLite file.
        """
        # Set default DB path if not provided
        if db_url is None:
            db_url = f'sqlite:///{self.DEFAULT_DB_PATH}'
        
        # For file-based SQLite, ensure the directory exists
        if db_url.startswith('sqlite:///') and not db_url == 'sqlite:///:memory:':
            db_path = db_url.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir:  # Only create directory if path is not in current directory
                os.makedirs(db_dir, exist_ok=True)
        
        self.db = init_db(db_url)
    
    def save_state(self, dojo, db_path=None):
        """
        Save the current state of the Dojo to a SQLite database.
        
        Args:
            dojo (Dojo): The Dojo instance to save
            db_path (str, optional): Path to the SQLite database file. 
                                   If None, uses the default path.
                                   
        Returns:
            bool: True if save was successful, False otherwise
        """
        session = None
        
        try:
            # Use default path if none provided
            if db_path is None:
                db_path = self.DEFAULT_DB_PATH
                
            # Check if the directory is writable
            db_dir = os.path.dirname(os.path.abspath(db_path))
            if db_dir:  # Only check if there's a directory component
                # First check if the directory exists and is writable
                if os.path.exists(db_dir):
                    if not os.access(db_dir, os.W_OK):
                        print(f"Error: Directory is not writable: {db_dir}")
                        return False
                else:
                    # If directory doesn't exist, try to create it
                    try:
                        os.makedirs(db_dir, exist_ok=False)  # Don't use exist_ok to catch race conditions
                        # Test if the directory is actually writable
                        test_file = os.path.join(db_dir, '.test_write')
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)
                    except (OSError, IOError) as e:
                        print(f"Error: Cannot create or write to directory: {db_dir}")
                        # Clean up the directory if we created it but can't write to it
                        if os.path.exists(db_dir) and not os.listdir(db_dir):
                            try:
                                os.rmdir(db_dir)
                            except OSError:
                                pass
                        return False
            
            # Format the database URL for SQLAlchemy
            abs_path = os.path.abspath(db_path)
            db_url = f'sqlite:///{abs_path}'.replace('\\', '/')  # Use forward slashes for SQLAlchemy
            
            # Check if the directory exists and is writable
            db_dir = os.path.dirname(abs_path)
            if db_dir:  # Only check if there's a directory component
                if not os.path.exists(db_dir):
                    print(f"Error: Directory does not exist: {db_dir}")
                    return False
                if not os.access(db_dir, os.W_OK):
                    print(f"Error: Directory is not writable: {db_dir}")
                    return False
                
                # Verify the directory is actually writable
                try:
                    test_file = os.path.join(db_dir, f'.test_write_{os.getpid()}')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                except (OSError, IOError) as e:
                    print(f"Error: Cannot write to directory: {db_dir}")
                    return False
            
            try:
                # Create a new database connection
                db = Database(db_url)
                db.create_tables()
                
                # Create a session
                Session = sessionmaker(bind=db.engine)
                session = Session()
            except Exception as e:
                print(f"Error creating database connection: {str(e)}")
                return False
            
            # Clear existing data in the right order to respect foreign key constraints
            session.query(FellowDB).delete()
            session.query(StaffDB).delete()
            session.query(PersonDB).delete()
            session.query(LivingSpaceDB).delete()
            session.query(OfficeDB).delete()
            session.query(RoomDB).delete()
            
            # Save rooms first
            for room in dojo.offices + dojo.living_spaces:
                db_room = to_db_room(room)
                session.add(db_room)
            
            # Save people after rooms
            for person in dojo.people:
                db_person = to_db_person(person)
                session.add(db_person)
            
            # Commit the transaction
            session.commit()
            
            # Verify the file was actually created
            if not os.path.exists(abs_path):
                print(f"Error: Database file was not created at {abs_path}", file=sys.stderr)
                return False
                
            return True
            
        except sqlalchemy.exc.SQLAlchemyError as e:
            if session is not None:
                session.rollback()
            print(f"Error saving state to database: {str(e)}", file=sys.stderr)
            return False
        except Exception as e:
            if session is not None:
                session.rollback()
            print(f"Error saving state to database: {str(e)}", file=sys.stderr)
            return False
        finally:
            if session is not None:
                session.close()
            # Close the database engine if it was created
            if db is not None and hasattr(db, 'engine'):
                db.engine.dispose()
    
    def load_state(self, dojo, db_path):
        """
        Load the state of the Dojo from a SQLite database.
        
        Args:
            dojo (Dojo): The Dojo instance to load data into
            db_path (str): Path to the SQLite database file
            
        Returns:
            bool: True if load was successful, False otherwise
        """
        session = None
        db = None
        
        try:
            # Check if the database file exists
            if not os.path.exists(db_path):
                print(f"Error: Database file '{db_path}' not found.")
                return False
                
            # Format the database URL for SQLAlchemy
            abs_path = os.path.abspath(db_path)
            db_url = f'sqlite:///{abs_path}'.replace('\\', '/')
            
            # Check if the file is a valid SQLite database
            if not self._is_valid_sqlite_db(abs_path):
                print("Error loading state from database: file is not a database")
                return False
                
            # Initialize database
            db = Database(db_url)
            
            # Create a session
            Session = sessionmaker(bind=db.engine)
            session = Session()
            
            # Clear existing data in the dojo
            dojo.offices = []
            dojo.living_spaces = []
            dojo.people = []
            dojo.staff = []
            dojo.fellows = []
            
            # Track loaded room names to prevent duplicates
            loaded_rooms = set()
            
            # Load rooms first
            room_dbs = session.query(RoomDB).all()
            for room_db in room_dbs:
                if room_db.name in loaded_rooms:
                    continue
                    
                room = to_domain_room(room_db, dojo)
                if room:
                    # Check if room already exists in the dojo before adding
                    if room.room_type == 'office':
                        if not any(r.name == room.name for r in dojo.offices):
                            dojo.offices.append(room)
                    else:
                        if not any(r.name == room.name for r in dojo.living_spaces):
                            dojo.living_spaces.append(room)
                    loaded_rooms.add(room_db.name)
            
            # Then load people
            person_dbs = session.query(PersonDB).all()
            for person_db in person_dbs:
                try:
                    # Check if person already exists in dojo.people
                    existing_person = next((p for p in dojo.people if p.person_id == person_db.id), None)
                    
                    if existing_person is None:
                        # Only create and add the person if they don't already exist
                        person = to_domain_person(person_db, dojo)
                        if not person:
                            continue
                            
                        # Add to appropriate role list
                        if person.person_type == 'FELLOW':
                            if person not in dojo.fellows:
                                dojo.fellows.append(person)
                        else:
                            if person not in dojo.staff:
                                dojo.staff.append(person)
                except Exception as e:
                    print(f"Error loading person {getattr(person_db, 'id', 'unknown')}: {str(e)}")
                    continue
            
            return True
                
        except sqlalchemy.exc.SQLAlchemyError as e:
            if session is not None:
                session.rollback()
            print(f"Database error loading state: {str(e)}", file=sys.stderr)
            return False
                
        except Exception as e:
            print(f"Error loading state: {str(e)}", file=sys.stderr)
            return False
            
        finally:
            if session is not None:
                session.close()
            # Close the database engine if it was created
            if db is not None and hasattr(db, 'engine'):
                db.engine.dispose()
    
    def _is_valid_sqlite_db(self, file_path):
        """Check if the given file is a valid SQLite database.
        
        Args:
            file_path (str): Path to the SQLite database file
            
        Returns:
            bool: True if the file is a valid SQLite database, False otherwise
        """
        if not os.path.isfile(file_path):
            return False
            
        # SQLite database files start with this header
        sqlite_header = b'SQLite format 3\000'
        
        try:
            with open(file_path, 'rb') as f:
                header = f.read(len(sqlite_header))
                return header == sqlite_header
        except (IOError, OSError):
            return False
            
    def _clear_database(self):
        """Clear all data from the database."""
        try:
            # Delete all data from all tables
            meta = Base.metadata
            for table in reversed(meta.sorted_tables):
                self.db.Session.execute(table.delete())
            self.db.Session.commit()
        except Exception as e:
            self.db.Session.rollback()
            raise e
