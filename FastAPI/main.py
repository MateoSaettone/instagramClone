from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

# .\env\Scripts\Activate
# uvicorn main:app --reload
# source env/bin/activate  # On mac

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class UserBase(BaseModel):
    username: str
    password: str

class PostBase(BaseModel):
    caption: str
    description: str
    likes: int
    image_url: str
    user_id: int
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


db_dependency = Annotated[Session, Depends(get_db)]

# Get all posts
@app.get("/posts/", status_code=status.HTTP_200_OK)
async def get_all_posts(db: db_dependency):
    posts = db.query(models.Post).all()
    return posts

# Post to database
@app.post("/posts/",status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()

# Get a post by id
@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post to get was not found")
    return post


# Delete a post by id
@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post to delete was not found")
    db.delete(db_post)
    db.commit()

# Post to database
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()

# Get a user by id
@app.get("/users/{users_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User to get not found")
    return user





