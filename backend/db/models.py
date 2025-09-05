from db.dbo import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, DateTime, func, Enum

import uuid
import enum

from datetime import datetime

class TimeBaseClass(Base):
    __abstract__ = True
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(TimeBaseClass):
    """
    Represents a user in the system.

    Fields:
        email: The email address of the user.
        username: The username of the user.
    """

    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(TimeBaseClass):
    """
    Represents a user session.

    Fields:
        user_id: The ID of the user who owns the session.
        name: The name of the session.
    """
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128), default="New Session")
    user: Mapped[User] = relationship("User", back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")


class RoleEnum(enum.Enum):
    """
    Enum for message roles.
    """
    user = "user"
    assistant = "assistant"
    system = "system"


class Message(TimeBaseClass):
    """
    Represents a message in a session.

    Fields:
        role: The role of the message sender ("user", "assistant", or "system").
        content: The textual content of the message.
    """
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, native_enum=False), nullable=False)
    content: Mapped[str] = mapped_column(Text)
    session: Mapped[Session] = relationship("Session", back_populates="messages")
