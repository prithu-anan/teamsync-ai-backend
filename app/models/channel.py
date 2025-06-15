from sqlalchemy import Column, Integer, String, ARRAY, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base
import enum

class ChannelType(enum.Enum):
    direct = "direct"
    group = "group"

class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(ChannelType), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    members = Column(ARRAY(Integer))
    messages = relationship("Message", back_populates="channel")