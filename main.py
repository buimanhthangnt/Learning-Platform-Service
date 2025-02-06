from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional, Dict
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from scraper import ContentScraper, YouTubeScraper
import uvicorn
from llm.base import BaseLLM
from llm.mockup_llm import MockupLLM
from llm.openai_llm import OpenAILLM
from llm.gemini_llm import GeminiLLM
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models, auth
from database import engine, get_db
from scraper.bing_scraper import BingSearchScraper
from scraper.jina_scraper import JinaContentExtractor

load_dotenv()

app = FastAPI()

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:8000"
).split(",")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    conversation: List[Dict[str, str]]

class Conversation(BaseModel):
    conversation: List[dict]

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Initialize LLM (use GeminiLLM instead of MockupLLM)
llm: BaseLLM = GeminiLLM()
content_scraper = ContentScraper()

# Initialize scrapers
youtube_scraper = YouTubeScraper()
bing_scraper = BingSearchScraper()
content_extractor = JinaContentExtractor()

# Create database tables
models.Base.metadata.create_all(bind=engine)

@app.post("/chat")
async def chat(chat_data: ChatMessage):
    try:
        response = await llm.chat(chat_data.conversation + [{"role": "user", "content": chat_data.message}])
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token = auth.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/generate-course")
async def generate_course(
    conversation: Conversation,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Generate course outline
        outline = await llm.generate_course_outline(conversation.conversation)
        
        # Find resources for each learning point in each topic
        topics_with_resources = []
        for topic in outline["topics"]:
            learning_points_with_resources = []
            
            for point in topic["learningPoints"]:
                print(f"Searching resources for learning point: {point['searchQuery']}")
                
                # Get YouTube videos
                videos = youtube_scraper.search_video(
                    point["searchQuery"],
                    max_results=2
                )
                
                # Get Bing search results
                articles = bing_scraper.search(point["searchQuery"])
                
                # Extract content from web pages
                web_content = []
                for article in articles:
                    content = content_extractor.extract_content(article["url"])
                    if content:
                        # Use Gemini to extract relevant information
                        processed_content = await llm.process_web_content(
                            content=content,
                            topic=point["title"],
                            context=point["description"]
                        )
                        if processed_content:
                            web_content.append({
                                "type": "article",
                                "title": article["title"],
                                "url": article["url"],
                                "content": processed_content,
                                "source": "Web"
                            })
                
                learning_point_with_resources = {
                    **point,
                    "resources": videos + web_content
                }
                learning_points_with_resources.append(learning_point_with_resources)
            
            topic_with_resources = {
                **topic,
                "learningPoints": learning_points_with_resources
            }
            topics_with_resources.append(topic_with_resources)
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/course/{course_id}")
async def get_course(
    course_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(models.Course).filter(
        models.Course.course_id == course_id,
        models.Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "id": course.course_id,
        "outline": course.outline,
        "createdAt": course.created_at.isoformat(),
        "updatedAt": course.updated_at.isoformat()
    }

@app.get("/user/courses")
async def get_user_courses(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    courses = db.query(models.Course).filter(
        models.Course.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": course.course_id,
            "outline": course.outline,
            "createdAt": course.created_at.isoformat(),
            "updatedAt": course.updated_at.isoformat()
        }
        for course in courses
    ]

def extract_topics(outline: str) -> List[str]:
    # Implement topic extraction logic
    pass

def generate_lesson(topic: str, content: dict) -> dict:
    # Implement lesson generation logic
    pass 


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)