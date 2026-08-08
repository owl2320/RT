from fastapi import HTTPException,Depends,Request,status
from passlib.context import CryptContext
from itsdangerous import URLSafeSerializer,BadSignature,SignatureExpired
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.user import get_user_by_id
from app.db.session import get_db

SESSION_COOKIE_NAME = "session"
_pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
_serializer = URLSafeSerializer(settings.SECRET_KEY,salt="session_key")

def hash_password(password:str) -> str:
    return _pwd_context.hash(password)

def verify_password(password:str,password_hash:str) -> bool:
    return _pwd_context.verify(password,password_hash)

def create_session_token(user_id:str)-> str:
    return _serializer.dumps(user_id)

def _decode_session_token(token:str)->str|None:
    try:
        return _serializer.loads(token,max_age=settings.SESSION_MAX_AGE)
    except (BadSignature,SignatureExpired):
        return None

def get_current_user(request:Request,db:Session=Depends(get_db)):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authenticated")

    user_id = _decode_session_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Session invalid or expired")

    user = get_user_by_id(db,user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User no longer exists")

    return user

