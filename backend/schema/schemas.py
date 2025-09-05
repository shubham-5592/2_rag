from typing import Optional, List
from pydantic import BaseModel
from pydantic import Field


class MessageIn(BaseModel):
    role: str
    content: str


class MessageOut(MessageIn):
    id: str
    created_at: str = Field(..., description="Timestamp in ISO 8601 format")


class SessionCreate(BaseModel):
    user_id: str
    name: Optional[str] = "New Session"


# class SessionUpdate(BaseModel):
#     name: Optional[str] = "New Session"


class SessionOut(BaseModel):
    id: str
    user_id: str
    # 'name' is not optional here because a session is expected to always have a name once created or updated.
    name: str
    user_id: str
    name: str


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    query: str


class SourceItem(BaseModel):
    # Define the expected fields for a source item
    # title: str
    source: str
    page: Optional[int] = None
    score: Optional[float] = None
    # Add other fields as needed

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    session_id: str


class HistoryOut(BaseModel):
    session_id: str
    messages: List[MessageOut]


class UserOut(BaseModel):
    id: str
    email: str
    username: str


class UserCreate(BaseModel):
    email: str
    username: str