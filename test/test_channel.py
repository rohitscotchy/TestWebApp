import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.DBConnection import Base, get_db


# ============================================================
# Test Database
# ============================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ============================================================
# Authentication
# ============================================================

def auth_headers():
    return {
        "Authorization": "Bearer test-token",
        "X-Client-Id": "test-client",
    }


# ============================================================
# Setup / Teardown
# ============================================================

@pytest.fixture(autouse=True)
def setup_and_teardown(monkeypatch):
    """Setup environment and database for each test."""

    # Force test authentication credentials
    monkeypatch.setenv(
        "API_BEARER_TOKEN",
        "test-token",
    )

    monkeypatch.setenv(
        "CLIENT_ID",
        "test-client",
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    yield

    # Remove tables
    Base.metadata.drop_all(bind=engine)


# ============================================================
# Tests
# ============================================================

class TestChannelEndpoints:

    def test_requires_authentication(self):

        response = client.post(
            "/Channel/channels",
            json={
                "name": "NoAuth",
                "device": "Device1",
                "project": "Project1",
            },
        )

        assert response.status_code == 401


    def test_invalid_bearer_token(self):

        headers = {
            "Authorization": "Bearer wrong-token",
            "X-Client-Id": "test-client",
        }

        response = client.post(
            "/Channel/channels",
            json={
                "name": "Test",
                "device": "Device1",
                "project": "Project1",
            },
            headers=headers,
        )

        assert response.status_code == 401


    def test_create_channel_success(self):

        channel_data = {
            "name": "Channel1",
            "device": "Device1",
            "project": "Project1",
        }

        response = client.post(
            "/Channel/channels",
            json=channel_data,
            headers=auth_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == channel_data["name"]
        assert data["device"] == channel_data["device"]
        assert data["project"] == channel_data["project"]
        assert "id" in data


    def test_create_channel_with_different_data(self):

        channel_data = {
            "name": "TestChannel",
            "device": "TestDevice",
            "project": "TestProject",
        }

        response = client.post(
            "/Channel/channels",
            json=channel_data,
            headers=auth_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == "TestChannel"
        assert data["device"] == "TestDevice"
        assert data["project"] == "TestProject"


    def test_create_channel_returns_id(self):

        channel_data = {
            "name": "ChannelWithID",
            "device": "DeviceID",
            "project": "ProjectID",
        }

        response = client.post(
            "/Channel/channels",
            json=channel_data,
            headers=auth_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert "id" in data
        assert isinstance(data["id"], int)
        assert data["id"] > 0


    def test_get_channels_empty(self):

        response = client.get(
            "/Channel/channels",
            headers=auth_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert data == []


    def test_get_channels_single(self):

        channel_data = {
            "name": "Channel1",
            "device": "Device1",
            "project": "Project1",
        }

        response = client.post(
            "/Channel/channels",
            json=channel_data,
            headers=auth_headers(),
        )

        assert response.status_code == 200

        response = client.get(
            "/Channel/channels",
            headers=auth_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["name"] == "Channel1"


    def test_get_channels_multiple(self):

        channels = [
            {
                "name": "Channel1",
                "device": "Device1",
                "project": "Project1",
            },
            {
                "name": "Channel2",
                "device": "Device2",
                "project": "Project2",
            },
            {
                "name": "Channel3",
                "device": "Device3",
                "project": "Project3",
            },
        ]

        for channel in channels:

            response = client.post(
                "/Channel/channels",
                json=channel,
                headers=auth_headers(),
            )

            assert response.status_code == 200

        response = client.get(
            "/Channel/channels",
            headers=auth_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 3

        names = [channel["name"] for channel in data]

        assert "Channel1" in names
        assert "Channel2" in names
        assert "Channel3" in names


    def test_create_and_get_channels_integration(self):

        channel1 = {
            "name": "Integration1",
            "device": "IntDevice1",
            "project": "IntProject1",
        }

        response1 = client.post(
            "/Channel/channels",
            json=channel1,
            headers=auth_headers(),
        )

        assert response1.status_code == 200

        channel1_id = response1.json()["id"]


        channel2 = {
            "name": "Integration2",
            "device": "IntDevice2",
            "project": "IntProject2",
        }

        response2 = client.post(
            "/Channel/channels",
            json=channel2,
            headers=auth_headers(),
        )

        assert response2.status_code == 200

        channel2_id = response2.json()["id"]


        response = client.get(
            "/Channel/channels",
            headers=auth_headers(),
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 2

        channel_ids = [channel["id"] for channel in data]

        assert channel1_id in channel_ids
        assert channel2_id in channel_ids