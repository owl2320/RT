import uuid
from datetime import datetime,timezone

from sqlalchemy import Column,String,Text,DateTime,ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base

def _uuid() -> str:
    """Generate an uuid everytime it is called"""
    return str(uuid.uuid4())

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String,primary_key=True,default=_uuid)
    user_id = Column(String,ForeignKey("users.id"),nullable=False)
    title = Column(String,nullable=True)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc))

    messages = relationship(
        "Message",
        back_populates="conversation",
        order_by="Message.created_at",
        cascade="all,delete-orphan"
    )

    user = relationship(
        "User",
        back_populates="conversations"
    )

class Message(Base):
    __tablename__ = "messages"

    id = Column(String,primary_key=True,default=_uuid)
    conversation_id = Column(String,ForeignKey("conversations.id"),nullable=False)
    role = Column(String,nullable=False)
    content = Column(Text,nullable=True)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc))

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

class User(Base):
    __tablename__ = "users"

    id = Column(String,primary_key=True,default=_uuid)
    email = Column(String,unique=True,nullable=False,index=True)
    password_hash = Column(String,nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversations = relationship(
        "Conversation",
        back_populates="user",
        order_by="Conversation.created_at",
        cascade="all, delete-orphan"
    )