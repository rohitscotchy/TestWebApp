from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.DBConnection import get_db
from src.app.models import Channel


router = APIRouter(
    prefix="/Channel",
    tags=["Channel"]
)


class ChannelRequest(BaseModel):
    name: str
    device: str
    project: str


@router.post("/channels")
def create_channel(
    channel: ChannelRequest,
    db: Session = Depends(get_db)
):
    new_channel = Channel(
        name=channel.name,
        device=channel.device,
        project=channel.project
    )

    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)

    return new_channel

@router.get("/channels")
def get_channels(
    db: Session = Depends(get_db)
):
    channels = db.query(Channel).all()

    return channels