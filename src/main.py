from fastapi import FastAPI

from src.DBConnection import engine, Base
from src.app import Channel
from src.app.models import Channel as ChannelModel


app = FastAPI()


@app.on_event("startup")
def startup():
    """Create database tables on startup"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create tables on startup: {e}")


# Register router
app.include_router(Channel.router)


@app.get("/")
def home():
    return {
        "message": "FastAPI application is running"
    }
