from sqlalchemy.orm import Session
from app.db.models import Conversation

def create_conversation(db: Session,user_id:str) -> Conversation:
    """Create a new conversation"""
    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation

def get_conversation(db: Session,user_id:str,conversation_id: str) -> Conversation|None:
    """Get a specific conversation of a user"""
    return (db.query(Conversation)
                    .filter(Conversation.id == conversation_id,Conversation.user_id == user_id)
                    .first())

def list_conversations(db: Session, user_id: str) -> list[Conversation]:
    """Return a list of all conversations of a user ordered by creation time"""
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.created_at).all()

def delete_conversation(db: Session, user_id:str, conversation_id: str) -> bool:
    """Delete a conversation"""
    conversation = get_conversation(db,user_id,conversation_id)
    if conversation is None:
        return False

    db.delete(conversation)
    db.commit()
    return True

def set_conversation_title(db: Session,user_id: str, conversation_id: str, title:str) -> Conversation|None:
    """Set the title of the conversation"""
    conversation = get_conversation(db,user_id,conversation_id)
    if conversation is None:
        return None
    conversation.title = title
    db.commit()
    db.refresh(conversation)
    return conversation

