from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    _instance = None
    _client = None
    _db = None
    _initialized = False

    def __new__(cls, connection_string: str = None, database_name: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, connection_string: str = None, database_name: str = None):
        if not self._initialized and connection_string and database_name:
            self.initialize_connection(connection_string, database_name)

    def initialize_connection(self, uri: str, database_name: str) -> None:
        try:
            if self._client is not None:
                logger.info("Database already initialized, skipping...")
                return

            self._client = MongoClient(uri)
            self._db = self._client[database_name]

            # Test connection
            self._client.admin.command('ping')
            self._initialized = True
            logger.info(f"Connected to MongoDB database: {database_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"MongoDB error during initialization: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {e}")
            raise

    @property
    def db(self):
        if self._db is None:
            raise RuntimeError("Database not initialized. Call initialize_connection() first.")
        return self._db
