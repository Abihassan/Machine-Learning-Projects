from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import pipeline
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# --- 1. Setup ML Model (Upgraded to unitary/toxic-bert) ---
print("Loading upgraded Machine Learning Model... (This will download once)")
# This model is much more reliable and doesn't require label-inversion math
toxicity_pipeline = pipeline("text-classification", model="unitary/toxic-bert")

# --- 2. Setup SQLite Database ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./comments.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBComment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    score = Column(Float)
    is_flagged = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- 3. Setup FastAPI ---
app = FastAPI()

class CommentRequest(BaseModel):
    text: str

# --- 4. API Endpoints ---
@app.post("/api/comments")
def submit_comment(comment: CommentRequest):
    # Run the text through the new ML model
    result = toxicity_pipeline(comment.text)[0]
    
    # Because unitary/toxic-bert only tracks toxic categories, 
    # the score directly represents the toxicity level. No math needed!
    score = result['score']
    
    # Threshold logic: Flag if toxicity score is > 0.65 (65%)
    is_flagged = score > 0.50

    # Save to database
    db = SessionLocal()
    new_comment = DBComment(
        text=comment.text,
        score=score,
        is_flagged=is_flagged
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    db.close()

    return {"status": "success", "is_flagged": is_flagged, "score": score}

@app.get("/api/comments")
def get_comments():
    db = SessionLocal()
    comments = db.query(DBComment).order_by(DBComment.timestamp.desc()).all()
    db.close()
    return comments

# --- 5. Serve Frontend ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r") as f:
        return f.read()