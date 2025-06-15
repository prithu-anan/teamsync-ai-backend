from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from sqlalchemy import text
from app.deps import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT NOW()"))
        current_time = result.scalar()  # Simple query to test DB
        return {"status": "healthy", "message": "Connected to database", "time":current_time}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}
