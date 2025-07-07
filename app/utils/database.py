from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    _instance = None
    _client = None
    _db = None

    # Generate a new instance of the class if needed
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # rename to initialize_connection
    def initialize(self, uri: str, database_name: str) -> None:
        try:
            self._client = MongoClient(uri)
            self._db = self._client[database_name]
            # Test connection
            self._client.admin.command('ping')
            logger.info(f"Connected to MongoDB database: {database_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @property
    def client(self) -> MongoClient:
        """Get MongoDB client"""
        if self._client is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._client

    @property
    def db(self):
        """Get database instance"""
        if self._db is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._db

    def close(self) -> None:
        """Close database connection"""
        if self._client:
            self._client.close()
            logger.info("Database connection closed")