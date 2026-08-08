from sqlalchemy.orm import Session
from app.db.models import User

def create_user(db: Session,email:str, password_hash:str) -> User:
    """Create a new user"""
    user = User(email=email,password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def get_user_by_id(db: Session, user_id: str) -> User|None:
    """Get the data of a user"""
    return db.get(User,user_id)

def get_user_by_email(db: Session, email: str) -> User|None:
    """Get the data of a user"""
    return db.query(User).filter(User.email == email).first()

def delete_user(db: Session,user_id: str) -> bool:
    """delete a user"""
    user = get_user_by_id(db,user_id)
    if user is None:
        return False

    db.delete(user)
    db.commit()

    return True