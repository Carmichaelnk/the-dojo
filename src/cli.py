"""
Command Line Interface for The Dojo - Office Space Allocation.
"""
import os
import sys
from docopt import docopt
from models.dojo import Dojo
from models.db.service import DatabaseService


class DojoApp:
    """Main application class for the Dojo CLI."""
    
    # Default database path (can be overridden)
    DEFAULT_DB_PATH = os.path.join(os.path.expanduser('~'), '.dojo', 'dojo.db')
    
    def __init__(self):
        """Initialize the Dojo application with a new Dojo instance."""
        self.dojo = Dojo()
        self.db_service = DatabaseService()
    
    def run(self):
        """Run the CLI application."""
        # Define the command line interface specification
        __doc__ = '''The Dojo - Office Space Allocation

        Usage:
          dojo create_room <room_type> <room_name>...
          dojo add_person <person_name> <FELLOW|STAFF> [wants_accommodation]
          dojo reallocate_person <person_identifier> <new_room_name>
          dojo load_people <filename>
          dojo print_room <room_name>
          dojo print_allocations [--o=filename]
          dojo print_unallocated [--o=filename]
          dojo save_state [--db=<sqlite_database>]
          dojo load_state <sqlite_database>
          dojo (-h | --help)
          dojo --version

        Options:
          -h --help         Show this screen.
          --version         Show version.
          -o=filename       Output to the specified file.
        
        Commands:
          create_room       Create rooms in the Dojo.
          add_person        Add a person to the Dojo and allocate them a room.
          print_room        Print all occupants of a room.
          print_allocations Print room allocations.
          print_unallocated Print unallocated people.
          save_state        Save the current state to a SQLite database.
          load_state        Load state from a SQLite database.
        
        Room Types:
          office            Office space (max 6 people).
          living_space      Living space (max 4 people, for fellows only).
        
        Database Options:
          --db=<sqlite_database>  Path to SQLite database file.
        
        Person Types:
          FELLOW            A fellow who can be allocated both office and living space.
          STAFF             A staff member who can only be allocated an office.
        
        Accommodation:
          Y                 For fellows who want living space.
          N                 For fellows who don't want living space (default).
        '''
        
        # Parse command line arguments
        args = docopt(__doc__, version='The Dojo 1.0')
        
        try:
            if args['create_room']:
                self.create_room(args['<room_type>'], args['<room_name>'])
            elif args['add_person']:
                self.add_person(
                    args['<person_name>'],
                    args['<FELLOW|STAFF>'],
                    args.get('<wants_accommodation>', 'N')
                )
            elif args['print_room']:
                self.print_room(args['<room_name>'])
            elif args['print_allocations']:
                self.print_allocations(args.get('--o'))
            elif args['print_unallocated']:
                self.print_unallocated(args.get('--o'))
            elif args['reallocate_person']:
                self.reallocate_person(args['<person_identifier>'], args['<new_room_name>'])
            elif args['load_people']:
                self.load_people(args['<filename>'])
            elif args['save_state']:
                self.save_state(args['--db'])
            elif args['load_state']:
                self.load_state(args['<sqlite_database>'])
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    def create_room(self, room_type, room_names):
        """
        Create one or more rooms in the Dojo.
        
        Args:
            room_type (str): Type of room to create ('office' or 'living_space')
            room_names (list): List of room names to create
            
        Returns:
            bool: True if any rooms were created, False otherwise
        """
        if room_type not in ['office', 'living_space']:
            print(f"Error: Invalid room type '{room_type}'. Must be 'office' or 'living_space'.")
            return False
            
        return self.dojo.create_room(room_type, room_names)
    
    def add_person(self, name, person_type, wants_accommodation="N"):
        """
        Add a person to the Dojo and allocate them rooms.
        
        Args:
            name (str): Person's name
            person_type (str): Type of person ('FELLOW' or 'STAFF')
            wants_accommodation (str): 'Y' if they want accommodation, 'N' otherwise
            
        Returns:
            bool: True if person was added successfully, False otherwise
        """
        person_type = person_type.upper()
        if person_type not in ['FELLOW', 'STAFF']:
            print(f"Error: Invalid person type '{person_type}'. Must be 'FELLOW' or 'STAFF'.")
            return False
            
        wants_accommodation = wants_accommodation.upper()
        if wants_accommodation not in ['Y', 'N']:
            print(f"Error: Invalid accommodation option '{wants_accommodation}'. Must be 'Y' or 'N'.")
            return False
            
        if person_type == 'STAFF' and wants_accommodation == 'Y':
            print("Error: Staff cannot be allocated living spaces.")
            return False
            
        return self.dojo.add_person(name, person_type, wants_accommodation)
    
    def print_room(self, room_name):
        """
        Print the names of all the people in the specified room.
        
        Args:
            room_name (str): Name of the room to print
        """
        room = None
        # Check offices
        for office in self.dojo.offices:
            if office.name.lower() == room_name.lower():
                room = office
                break
        
        # If not found in offices, check living spaces
        if not room:
            for living_space in self.dojo.living_spaces:
                if living_space.name.lower() == room_name.lower():
                    room = living_space
                    break
        
        if not room:
            print(f"Room '{room_name}' not found.")
            return
        
        print(f"Room: {room.name}")
        print("Type:", "Office" if room.room_type == "office" else "Living Space")
        print("Occupants:")
        for occupant_id in room.occupants:
            # Find person by ID
            person = next((p for p in self.dojo.people if p.person_id == occupant_id), None)
            if person:
                print(f"  - {person.name} ({person.person_type})")
    
    def print_allocations(self, filename=None):
        """
        Print a list of allocations to screen or file.
        
        Args:
            filename (str, optional): If provided, output will be written to this file
        """
        output = []
        
        # Add offices
        if self.dojo.offices:
            output.append("OFFICES")
            output.append("=" * 50)
            for office in self.dojo.offices:
                output.append(f"\n{office.name} ({len(office.occupants)}/{office.capacity}):")
                for occupant_id in office.occupants:
                    person = next((p for p in self.dojo.people if p.person_id == occupant_id), None)
                    if person:
                        output.append(f"  - {person.name}")
        
        # Add living spaces
        if self.dojo.living_spaces:
            output.append("\nLIVING SPACES")
            output.append("=" * 50)
            for living_space in self.dojo.living_spaces:
                output.append(f"\n{living_space.name} ({len(living_space.occupants)}/{living_space.capacity}):")
                for occupant_id in living_space.occupants:
                    person = next((p for p in self.dojo.people if p.person_id == occupant_id), None)
                    if person:
                        output.append(f"  - {person.name}")
        
        # If no allocations yet
        if not output:
            output = ["No room allocations to display."]
        
        # Print or write to file
        if filename:
            with open(filename, 'w') as f:
                f.write("\n".join(output))
        else:
            print("\n".join(output))
    
    def reallocate_person(self, person_id, new_room_name):
        """
        Reallocate a person to a different room.
        
        Args:
            person_id (str): ID of the person to reallocate
            new_room_name (str): Name of the room to move the person to
            
        Returns:
            bool: True if reallocation was successful, False otherwise
        """
        # Find the person by ID
        person = next((p for p in self.dojo.people if p.person_id == person_id), None)
        if not person:
            print(f"Error: Person with ID '{person_id}' not found.")
            return False
            
        # Find the new room (check both offices and living spaces)
        new_room = None
        new_room_type = None
        
        # Check offices first
        for office in self.dojo.offices:
            if office.name.lower() == new_room_name.lower():
                new_room = office
                new_room_type = 'office'
                break
        
        # If not found in offices, check living spaces
        if not new_room:
            for living_space in self.dojo.living_spaces:
                if living_space.name.lower() == new_room_name.lower():
                    # Only allow living space reallocation for Fellows who want accommodation
                    if person.person_type == 'FELLOW' and person.wants_accommodation:
                        new_room = living_space
                        new_room_type = 'living_space'
                    else:
                        print("Error: Only Fellows who have requested accommodation can be allocated to living spaces.")
                        return False
                    break
        
        if not new_room:
            print(f"Error: Room '{new_room_name}' not found or not suitable for this person.")
            return False
            
        # Check if the new room is full
        if len(new_room.occupants) >= new_room.capacity:
            print(f"Error: {new_room.name} is already at full capacity.")
            return False
            
        # Find the person's current room of the same type
        current_room = None
        rooms_to_check = self.dojo.offices if new_room_type == 'office' else self.dojo.living_spaces
        
        for room in rooms_to_check:
            if person_id in room.occupants:
                current_room = room
                break
        
        # If person is already in the target room
        if current_room and current_room.name.lower() == new_room.name.lower():
            print(f"{person.name} is already in {new_room.name}.")
            return False
            
        # Perform the reallocation
        try:
            # Remove from current room if any
            if current_room:
                current_room.occupants.remove(person_id)
                
                # Update allocation status based on room type
                if current_room.room_type == 'office':
                    person.office_allocated = False
                elif current_room.room_type == 'living_space':
                    person.living_space_allocated = False
            
            # Add to new room
            new_room.occupants.append(person_id)
            
            # Update person's allocation status
            if new_room.room_type == 'office':
                person.office_allocated = True
            else:
                person.living_space_allocated = True
                
            print(f"{person.name} has been reallocated to {new_room.name}.")
            return True
            
        except Exception as e:
            print(f"Error during reallocation: {str(e)}")
            return False
    
    def load_people(self, filename):
        """
        Load people from a text file and add them to the Dojo.
        
        Args:
            filename (str): Path to the file containing people data
            
        Returns:
            bool: True if any people were added successfully, False otherwise
        """
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                
            added_count = 0
            for line in lines:
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Parse the line (format: FIRSTNAME LASTNAME PERSON_TYPE [ACCOMMODATION])
                parts = line.split()
                if len(parts) < 2:  # At least first name and type needed
                    print(f"Warning: Invalid line format: {line}")
                    continue
                    
                # Extract person type (last part or second last part)
                if parts[-1].upper() in ['Y', 'N']:
                    wants_accommodation = parts[-1].upper()
                    person_type = parts[-2].upper()
                    name = ' '.join(parts[:-2])
                else:
                    wants_accommodation = 'N'  # Default to 'N' if not specified
                    person_type = parts[-1].upper()
                    name = ' '.join(parts[:-1])
                
                # Validate person type
                if person_type not in ['FELLOW', 'STAFF']:
                    print(f"Warning: Invalid person type '{person_type}' in line: {line}")
                    continue
                    
                # Add the person
                success = self.add_person(
                    name=name,
                    person_type=person_type,
                    wants_accommodation=wants_accommodation
                )
                
                if success:
                    added_count += 1
            
            if added_count > 0:
                print(f"Successfully added {added_count} people from {filename}")
                return True
            else:
                print("No valid people were added from the file.")
                return False
                
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except Exception as e:
            print(f"Error reading file '{filename}': {str(e)}")
            return False
    
    def print_unallocated(self, filename=None):
        """
        Print a list of unallocated people to screen or file.
        
        Args:
            filename (str, optional): If provided, output will be written to this file
        """
        unallocated = []
        
        for person in self.dojo.people:
            if not person.office_allocated or \
               (hasattr(person, 'wants_accommodation') and 
                person.wants_accommodation and 
                not person.living_space_allocated):
                unallocated.append(person)
        
        output = ["Unallocated People", "=" * 50]
        if not unallocated:
            output.append("No unallocated people.")
        else:
            for person in unallocated:
                reasons = []
                if not person.office_allocated:
                    reasons.append("office")
                if (hasattr(person, 'wants_accommodation') and 
                    person.wants_accommodation and 
                    not person.living_space_allocated):
                    reasons.append("living space")
                output.append(f"- {person.name} (missing: {', '.join(reasons)})")
        
        # Print or write to file
        if filename:
            with open(filename, 'w') as f:
                f.write('\n'.join(output) + '\n')
            print(f"Unallocated people list saved to {filename}")
        else:
            print('\n'.join(output))
        
        return bool(unallocated)
    
    def save_state(self, db=None):
        """
        Save the current state of the Dojo to a SQLite database.
        
        Args:
            db (str, optional): Path to the SQLite database file.
                              If not provided, uses the default location.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            db_path = db if db is not None else self.DEFAULT_DB_PATH
            db_path = os.path.abspath(db_path)
            db_dir = os.path.dirname(db_path)
            
            # If the directory doesn't exist, return False
            if not os.path.exists(db_dir):
                print(f"Error: Directory does not exist: {db_dir}")
                return False
            
            # Check if the directory is writable
            if not os.access(db_dir, os.W_OK):
                print(f"Error: Directory is not writable: {db_dir}")
                return False
                
            # If we get here, the directory exists and is writable
            try:
                # Test if we can write to the directory
                test_file = os.path.join(db_dir, f".test_write_{os.getpid()}")
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except (OSError, IOError) as e:
                print(f"Error: Cannot write to directory: {db_dir}")
                return False
            
            # Try to save to the database
            try:
                success = self.db_service.save_state(self.dojo, db_path)
                if success:
                    print(f"State saved to {db_path}")
                    return True
                return False
            except Exception as e:
                print(f"Error saving state to database: {str(e)}")
                return False
                
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return False
    
    def load_state(self, db_path):
        """
        Load the state of the Dojo from a SQLite database.
        
        Args:
            db_path (str): Path to the SQLite database file.
        
        Returns:
            bool: True if load was successful, False otherwise
        """
        try:
            # Check if the database file exists
            if not os.path.exists(db_path):
                print(f"Error: Database file '{db_path}' not found.")
                return False
                
            # Check if the file is a valid SQLite database
            if not self.db_service._is_valid_sqlite_db(db_path):
                print("Error loading state from database: file is not a database")
                return False
                
            # Clear existing data in the dojo before loading
            self.dojo = Dojo()
            
            success = self.db_service.load_state(self.dojo, db_path)
            if success:
                print(f"State loaded from {db_path}")
                return True
            return False
        except Exception as e:
            print(f"Error loading state from database: {str(e)}")
            return False


def main():
    """Entry point for the Dojo application."""
    app = DojoApp()
    app.run()


if __name__ == '__main__':
    main()
