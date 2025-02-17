from fastapi import APIRouter, HTTPException, Depends
from models import models 
from models.database import get_db
from models.pydantic import *
from sqlalchemy.orm import Session
from services.lp_generate.v1.lp_generate_v1 import LPGenerateV1
from services.auth import auth_service as auth
from services.llm.gemini import GeminiLLM
import uuid


router = APIRouter()

llm_model = GeminiLLM()
lp_generate = LPGenerateV1(llm_model)


@router.post("/chat")
async def chat(chat_data: ChatMessage):
    try:
        response = await lp_generate.chat(chat_data.conversation + [{"role": "user", "content": chat_data.message}])
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-course")
async def generate_course(
    conversation: Conversation,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Generate course outline
    outline = await lp_generate.generate_course_outline(conversation.conversation)
    topics_with_resources = await lp_generate.generate_topic_with_resources(outline)
    
    # Create final course structure
    course_data = {
        **outline,
        "topics": topics_with_resources
    }
    
    # Save to database
    course_id = str(uuid.uuid4())
    db_course = models.Course(
        course_id=course_id,
        user_id=current_user.id,
        outline=course_data,
        lessons=[]
    )
    db.add(db_course)
    db.commit()
    
    return {
        "id": course_id,
        "outline": course_data,
        "createdAt": db_course.created_at.isoformat(),
        "updatedAt": db_course.updated_at.isoformat()
    }
    
