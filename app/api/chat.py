import logging

from fastapi import APIRouter,HTTPException,Depends,status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json

from app.schemas.chat import ChatRequest,ChatResponse
from app.schemas.conversation import ConversationPreview,ConversationDetail,ConversationUpdate
from app.services.llm_service import chat,stream_chat,generate_title
from app.db.session import get_db

from app.crud.conversation import (get_conversation, create_conversation, set_conversation_title,
                                   list_conversations,delete_conversation)

from app.crud.message import add_message,get_history

from app.db.models import User,Conversation
from app.core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/chat',tags=['chat'])

def _get_or_create_conversation(db:Session,user_id:str,conversation_id:str|None) -> Conversation:
    """Get an existing conversation or create a new conversation"""
    if conversation_id:
        conversation = get_conversation(db,user_id,conversation_id)
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Conversation Not Found.")
        return conversation

    return create_conversation(db,user_id)

def _generate_title(db:Session, conversation:Conversation, message:str) -> None:
    """Generate title for a conversation"""
    if conversation.title is None:
        title = generate_title(message)
        set_conversation_title(db,conversation.user_id,conversation.id,title)

@router.get('/conversations',response_model=ConversationPreview)
def list_chat(db: Session = Depends(get_db),user: User = Depends(get_current_user)):
    """Return a list of all conversations of a user"""
    return list_conversations(db,user.id)

@router.get('/conversations/{conversation_id}',response_model=ConversationDetail)
def get_chat(conversation_id:str,db: Session = Depends(get_db),user: User = Depends(get_current_user)):
    """Get any specific conversation"""
    conversation = get_conversation(db,user.id,conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Conversation Not Found")
    return conversation

@router.delete('/conversations/{conversation_id}')
def delete_chat(conversation_id: str,db: Session = Depends(get_db),user: User = Depends(get_current_user)):
    """Delete any specific conversation"""

    deleted = delete_conversation(db,user.id,conversation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return {"message":"Conversation deleted"}

@router.patch('/conversations/{conversation_id}',response_model=ConversationDetail)
def update_chat(conversation_id:str,data:ConversationUpdate,
                        db: Session=Depends(get_db),user:User=Depends(get_current_user)):
    """Update any conversation"""

    conversation = set_conversation_title(db,user.id,conversation_id,data.title)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Conversation not found.")
    return conversation


#Not used rlly anymore
@router.post('/',response_model=ChatResponse)
def create_chat(request: ChatRequest, user: User = Depends(get_current_user) ,db: Session = Depends(get_db)):
    """Create a chat one at a time instead of streaming it"""
    if request.conversation_id:
        conversation = get_conversation(db,user.id,request.conversation_id)
        #if conversation id isn't found
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation Not Found."
            )
    else:
        conversation = create_conversation(db,user.id)

    add_message(db,conversation_id=conversation.id,role="user",content=request.message)

    history = get_history(db,conversation_id=conversation.id)
    reply = chat(history)
    add_message(db,conversation_id=conversation.id,role="assistant",content=reply)

    return ChatResponse(
        conversation_id=conversation.id,
        reply = reply
    )

@router.post('/stream')
def stream(request: ChatRequest, user: User = Depends(get_current_user),db:Session = Depends(get_db)):
    """Stream chat responses"""
    conversation = _get_or_create_conversation(db,user.id,request.conversation_id)
    add_message(db, conversation_id=conversation.id, role="user", content=request.message)
    history = get_history(db,conversation_id=conversation.id)

    def event_generator():
        full_reply = ""
        yield f"data: {json.dumps({"type":"conversation","id":conversation.id})}\n\n"
        try:
            for chunk in stream_chat(history):
                full_reply += chunk
                yield f"data: {json.dumps({"type": "token","content": chunk})}\n\n"

            add_message(db,conversation_id=conversation.id,role="assistant",content=full_reply)
        except Exception:
            logger.exception("Streaming failed")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Something went wrong'})}\n\n"
        finally:
            yield f"data: {json.dumps({"type": "done",})}\n\n"

        _generate_title(db,conversation,request.message)

    return StreamingResponse(event_generator(),media_type='text/event-stream',
                             headers={"Cache-Control": "no-cache","X-Accel-Buffering": "no"})

