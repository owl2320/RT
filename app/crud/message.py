from fastapi import HTTPException,status
from app.db.models import Message, Conversation
from sqlalchemy.orm import Session

def add_message(db:Session,conversation_id:str,role:str,content:str) -> Message:
    message = Message(conversation_id=conversation_id,role=role,content=content)
    db.add(message)
    db.commit()
    return message

def get_history(db:Session,conversation_id:str) -> list[dict]:
    conversation = db.get(Conversation,conversation_id)
    #raise error if conversation is not found
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    history = [{"role":m.role,"content":m.content} for m in conversation.messages]

    #DEBUG
    # print(history)
    return history