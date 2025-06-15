from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    thread_parent_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    sender = relationship("User", foreign_keys=[sender_id])
    channel = relationship("Channel", back_populates="messages")
    recipient = relationship("User", foreign_keys=[recipient_id])
    __table_args__ = (
        CheckConstraint('channel_id IS NOT NULL OR recipient_id IS NOT NULL', name='channel_or_recipient'),
    )