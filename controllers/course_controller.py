from fastapi import APIRouter, HTTPException, Depends
from models import models 
from models.database import get_db
from models.pydantic import *
from sqlalchemy.orm import Session
from services.auth import auth_service as auth


router = APIRouter()


@router.get("/course/{course_id}")
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


@router.get("/user/courses")
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


@router.delete("/course/{course_id}")
async def delete_course(
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
    
    db.delete(course)
    db.commit()
    
    return {"message": "Course deleted successfully"}

