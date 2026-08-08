from pydantic import BaseModel,EmailStr
from datetime import datetime

class UserResponse(BaseModel):
    id:str
    email:EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

