from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import DB_URL
from database.models import Base
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    _engine = None
    _session_maker = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connection and create all tables"""
        try:
            self._engine = create_engine(
                DB_URL,
                connect_args={"check_same_thread": False},
                echo=False
            )
            self._session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
            Base.metadata.create_all(bind=self._engine)
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_session(self) -> Session:
        """Get a new database session"""
        if self._session_maker is None:
            self._initialize()
        return self._session_maker()

    def close_session(self, session: Session):
        """Close a database session"""
        if session:
            session.close()

    @staticmethod
    def get_db():
        """Static method for dependency injection in Streamlit apps"""
        db = DatabaseConnection()
        session = db.get_session()
        try:
            yield session
        finally:
            session.close()


# Singleton instance
db_connection = DatabaseConnection()


def get_session():
    """Convenience function to get a session"""
    return db_connection.get_session()
