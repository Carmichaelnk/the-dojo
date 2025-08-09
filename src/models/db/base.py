"""
Base database models for The Dojo application.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Database:
    """Database connection and session management."""
    
    def __init__(self, db_url='sqlite:///dojo.db'):
        """Initialize database connection.
        
        Args:
            db_url (str): Database URL. Defaults to SQLite in-memory database.
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.Session()
