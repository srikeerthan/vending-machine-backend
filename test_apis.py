from fastapi.testclient import TestClient

from app.core.config import get_app_settings
from app.main import app

# Set up the TestClient
client = TestClient(app)

settings = get_app_settings()

# Set up the in-memory SQLite database for testing
settings.database_url = "sqlite:///:memory:"
