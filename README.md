# The Dojo - Office Space Allocation System

## Overview
A Python-based system for automatically allocating office and living spaces to Andela Kenya's Dojo facility members.

## Features
- Random allocation of office spaces to Staff and Fellows
- Optional living space allocation for Fellows
- Capacity management (Office: 6 people, Living Space: 4 people)
- Object-oriented design with proper class hierarchy

## Project Structure
```
the-dojo/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── person.py
│   │   ├── fellow.py
│   │   ├── staff.py
│   │   ├── room.py
│   │   ├── office.py
│   │   ├── living_space.py
│   │   └── dojo.py
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_*.py files
├── designs/
│   └── uml_diagrams/
├── requirements.txt
└── README.md
```

## Requirements
- Python 3.8+
- pytest for testing

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from src.models.dojo import Dojo

# Create Dojo instance
dojo = Dojo()

# Add rooms
dojo.create_room("office", "Blue Office")
dojo.create_room("living_space", "Red Living Space")

# Add people
dojo.add_person("John Doe", "Fellow", wants_accommodation="Y")
dojo.add_person("Jane Smith", "Staff")
```

## Testing
```bash
pytest tests/
```

## Development Approach
This project follows Test-Driven Development (TDD) principles:
1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor and improve
4. Repeat

## Tasks Progress
- [ ] Task 0: Project setup and basic structure
- [ ] Task 1: Core class implementation
- [ ] Task 2: Room allocation logic
- [ ] Task 3: Advanced features and validation
- [ ] Task 4: Final enhancements and documentation
