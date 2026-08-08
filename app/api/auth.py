from sqlalchemy.orm import Session
from fastapi import Response, HTTPException, status, Depends, APIRouter

from app.core.config import settings
from app.db.session import get_db
from app.crud.user import create_user,get_user_by_email
from app.core.security import hash_password,verify_password,create_session_token,SESSION_COOKIE_NAME
from app.core.security import get_current_user
from app.schemas.user import UserResponse
from app.schemas.auth import SignUpRequest,LoginRequest
from app.db.models import User

router = APIRouter(prefix="/auth",tags=["auth"])

def _set_session_cookie(response:Response,user_id:str)->None:
    token = create_session_token(user_id)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
        max_age=settings.SESSION_MAX_AGE,
        path="/"
    )

@router.post('/signup',response_model=UserResponse)
def signup(request: SignUpRequest,response: Response,db: Session = Depends(get_db)):
    if get_user_by_email(db,request.email) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already registered")

    user = create_user(db,request.email,hash_password(request.password))
    _set_session_cookie(response,user.id)
    return user

@router.post('/login',response_model=UserResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_email(db,request.email)

    if user is None or not verify_password(request.password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid email or password")

    _set_session_cookie(response,user.id)
    return user

# @router.get("/me", response_model=UserResponse)
# def me(user: User = Depends(get_current_user)):
#     """Who's currently logged in — used by the frontend to show identity in the header."""
#     return user

@router.post('/logout')
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"status":"logged out"}