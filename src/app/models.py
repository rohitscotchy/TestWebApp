from sqlalchemy import Column, Integer, String

from src.DBConnection import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    device = Column(String(100), nullable=False)
    project = Column(String(100), nullable=False)
