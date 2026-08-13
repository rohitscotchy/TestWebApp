from fastapi import FastAPI

from src.DBConnection import engine, Base
from src.app import Channel
from src.app.models import Channel as ChannelModel


app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Register router
app.include_router(Channel.router)


@app.get("/")
def home():
    return {
        "message": "FastAPI application is running"
    }