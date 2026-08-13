import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.DBConnection import Base, get_db
from src.app.models import Channel


# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Create tables before each test
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after each test
    Base.metadata.drop_all(bind=engine)


class TestChannelEndpoints:
    """Test cases for Channel endpoints"""

    def test_create_channel_success(self):
        """Test successfully creating a channel"""
        channel_data = {
            "name": "Channel1",
            "device": "Device1",
            "project": "Project1"
        }
        response = client.post("/Channel/channels", json=channel_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == channel_data["name"]
        assert data["device"] == channel_data["device"]
        assert data["project"] == channel_data["project"]
        assert "id" in data

    def test_create_channel_with_different_data(self):
        """Test creating a channel with different data"""
        channel_data = {
            "name": "TestChannel",
            "device": "TestDevice",
            "project": "TestProject"
        }
        response = client.post("/Channel/channels", json=channel_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TestChannel"
        assert data["device"] == "TestDevice"
        assert data["project"] == "TestProject"

    def test_get_channels_empty(self):
        """Test getting channels when database is empty"""
        response = client.get("/Channel/channels")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_channels_single(self):
        """Test getting channels with one channel in database"""
        # Create a channel
        channel_data = {
            "name": "Channel1",
            "device": "Device1",
            "project": "Project1"
        }
        client.post("/Channel/channels", json=channel_data)

        # Get channels
        response = client.get("/Channel/channels")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Channel1"
        assert data[0]["device"] == "Device1"
        assert data[0]["project"] == "Project1"

    def test_get_channels_multiple(self):
        """Test getting multiple channels"""
        channels_data = [
            {
                "name": "Channel1",
                "device": "Device1",
                "project": "Project1"
            },
            {
                "name": "Channel2",
                "device": "Device2",
                "project": "Project2"
            },
            {
                "name": "Channel3",
                "device": "Device3",
                "project": "Project3"
            }
        ]

        # Create multiple channels
        for channel_data in channels_data:
            response = client.post("/Channel/channels", json=channel_data)
            assert response.status_code == 200

        # Get all channels
        response = client.get("/Channel/channels")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Verify all channels are present
        names = [channel["name"] for channel in data]
        assert "Channel1" in names
        assert "Channel2" in names
        assert "Channel3" in names

    def test_create_channel_returns_id(self):
        """Test that created channel returns an ID"""
        channel_data = {
            "name": "ChannelWithID",
            "device": "DeviceID",
            "project": "ProjectID"
        }
        response = client.post("/Channel/channels", json=channel_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_create_and_get_channels_integration(self):
        """Integration test for creating and retrieving channels"""
        # Create first channel
        channel1_data = {
            "name": "Integration1",
            "device": "IntDevice1",
            "project": "IntProject1"
        }
        response1 = client.post("/Channel/channels", json=channel1_data)
        channel1_id = response1.json()["id"]

        # Create second channel
        channel2_data = {
            "name": "Integration2",
            "device": "IntDevice2",
            "project": "IntProject2"
        }
        response2 = client.post("/Channel/channels", json=channel2_data)
        channel2_id = response2.json()["id"]

        # Get all channels
        response = client.get("/Channel/channels")
        assert response.status_code == 200
        data = response.json()

        # Verify both channels are in the response
        assert len(data) == 2
        channel_ids = [channel["id"] for channel in data]
        assert channel1_id in channel_ids
        assert channel2_id in channel_ids
