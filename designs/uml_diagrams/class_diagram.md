# The Dojo - UML Class Diagram

## Class Hierarchy Overview

```
Person (Abstract Base Class)
├── Fellow
└── Staff

Room (Abstract Base Class)
├── Office
└── LivingSpace

Dojo (Main Controller Class)
```

## Detailed Class Specifications

### Person (Abstract Base Class)
```
Person
├── Attributes:
│   ├── name: str
│   ├── person_id: str (auto-generated)
│   └── person_type: str
├── Methods:
│   ├── __init__(name: str)
│   └── __str__() -> str
```

### Fellow (Inherits from Person)
```
Fellow
├── Attributes:
│   ├── wants_accommodation: bool
│   ├── office_allocated: str (room name or None)
│   └── living_space_allocated: str (room name or None)
├── Methods:
│   └── __init__(name: str, wants_accommodation: str = "N")
```

### Staff (Inherits from Person)
```
Staff
├── Attributes:
│   └── office_allocated: str (room name or None)
├── Methods:
│   └── __init__(name: str)
```

### Room (Abstract Base Class)
```
Room
├── Attributes:
│   ├── name: str
│   ├── room_type: str
│   ├── capacity: int
│   └── occupants: List[str] (person IDs)
├── Methods:
│   ├── __init__(name: str)
│   ├── add_occupant(person_id: str) -> bool
│   ├── remove_occupant(person_id: str) -> bool
│   ├── is_full() -> bool
│   └── available_space() -> int
```

### Office (Inherits from Room)
```
Office
├── Attributes:
│   └── capacity: int = 6
├── Methods:
│   └── __init__(name: str)
```

### LivingSpace (Inherits from Room)
```
LivingSpace
├── Attributes:
│   └── capacity: int = 4
├── Methods:
│   └── __init__(name: str)
```

### Dojo (Main Controller)
```
Dojo
├── Attributes:
│   ├── offices: List[Office]
│   ├── living_spaces: List[LivingSpace]
│   ├── fellows: List[Fellow]
│   ├── staff: List[Staff]
│   └── all_people: Dict[str, Person] (person_id -> Person)
├── Methods:
│   ├── __init__()
│   ├── create_room(room_type: str, room_name: str) -> str
│   ├── add_person(name: str, person_type: str, wants_accommodation: str = "N") -> str
│   ├── allocate_office(person: Person) -> str
│   ├── allocate_living_space(fellow: Fellow) -> str
│   ├── print_room(room_name: str) -> str
│   ├── print_allocations(filename: str = None) -> str
│   ├── print_unallocated(filename: str = None) -> str
│   ├── reallocate_person(person_id: str, new_room_name: str) -> str
│   └── load_people(filename: str) -> str
```

## Relationships
- Person is the base class for Fellow and Staff (Inheritance)
- Room is the base class for Office and LivingSpace (Inheritance)
- Dojo has a composition relationship with all other classes (Aggregation)
- Each Room contains a list of Person IDs (Association)
- Each Person can be allocated to one Office and optionally one LivingSpace (Association)

## Key Design Decisions
1. **Abstract Base Classes**: Person and Room are abstract to enforce common interface
2. **Unique IDs**: Each person gets a unique ID for tracking allocations
3. **Separation of Concerns**: Dojo handles all allocation logic, rooms handle capacity
4. **Flexible Storage**: Using lists and dictionaries for efficient lookups
5. **Type Safety**: Clear distinction between Fellows and Staff for allocation rules
