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
    username: str
    user_id: int
    image_url: str
    description: str
    likes: int

class StoryBase(BaseModel):
    image_url: str
    username: str

class UserUpdate(BaseModel):
    username: str
    password: str

class PostUpdate(BaseModel):
    username: str
    user_id: int
    image_url: str
    description: str
    likes: int

class StoryUpdate(BaseModel):
    image_url: str
    username: str
   
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

# Update a post by id
@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(post_id: int, post_update: PostUpdate, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post to update was not found")
    for key, value in post_update.dict().items():
        setattr(db_post, key, value)
    db.commit()
    return db_post

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

# Get all users
@app.get("/users/", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency):
    users = db.query(models.User).all()
    return users

# Get a user by id
@app.get("/users/{users_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User to get not found")
    return user

# Update a user by id
@app.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_update: UserUpdate, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User to update was not found")
    for key, value in user_update.dict().items():
        setattr(db_user, key, value)
    db.commit()
    return db_user

# Delete a user by id
@app.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User to delete was not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}

# Get all stories
@app.get("/stories/", status_code=status.HTTP_200_OK)
async def get_all_stories(db: db_dependency):
    stories = db.query(models.Story).all()
    return stories

# Get a story by id
@app.get("/stories/{story_id}", status_code=status.HTTP_200_OK)
async def read_story(story_id: int, db: db_dependency):
    story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

# Update a story by id
@app.put("/stories/{story_id}", status_code=status.HTTP_200_OK)
async def update_story(story_id: int, story_update: StoryUpdate, db: db_dependency):
    db_story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    for key, value in story_update.dict().items():
        setattr(db_story, key, value)
    db.commit()
    return db_story

# Delete a story by id
@app.delete("/stories/{story_id}", status_code=status.HTTP_200_OK)
async def delete_story(story_id: int, db: db_dependency):
    db_story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    db.delete(db_story)
    db.commit()
    return {"detail": "Story deleted successfully"}


