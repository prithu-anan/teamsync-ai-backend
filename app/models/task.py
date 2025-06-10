from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.db import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum('backlog', 'todo', 'in_progress', 'in_review', 'blocked', 'completed', name='task_status'), nullable=False)
    deadline = Column(DateTime(timezone=True))
    priority = Column(Enum('low', 'medium', 'high', 'urgent', name='task_priority'))
    time_estimate = Column(String(50))
    ai_time_estimate = Column(String(50))
    ai_priority = Column(Enum('low', 'medium', 'high', 'urgent', name='task_priority'))
    smart_deadline = Column(DateTime(timezone=True))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_by = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime(timezone=True))
    parent_task_id = Column(Integer, ForeignKey("tasks.id"))
    attachments = Column(ARRAY(Text))

    project = relationship("Project", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent_task")