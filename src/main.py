from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.DBConnection import engine, Base
from src.app import Channel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # Startup
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Warning: Could not create tables on startup: {e}")

    yield

    # Shutdown
    print("Application shutting down.")


app = FastAPI(
    title="Test Web App",
    description="FastAPI application for Channel management",
    version="1.0.0",
    lifespan=lifespan,
)


# Register router
app.include_router(Channel.router)


@app.get("/")
def home():
    return {
        "message": "FastAPI application is running"
    }