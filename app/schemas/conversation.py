from pydantic import BaseModel
from datetime import datetime

class ConversationPreview(BaseModel):
    id: str
    title:str|None
    created_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    role: str
    content:str|None
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationDetail(BaseModel):
    id: str
    title:str|None
    messages:list[MessageResponse]
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationUpdate(BaseModel):
    title: str | None = None

    class Config:
        from_attributes = True

