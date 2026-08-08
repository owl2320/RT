from pydantic import BaseModel,EmailStr

class SignUpRequest(BaseModel):
    email:EmailStr
    password:str

class LoginRequest(BaseModel):
    email:EmailStr
    password:str