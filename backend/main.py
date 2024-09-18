# Import necessary modules and libraries for building the API
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from models import User
import pytz

# Create a FastAPI instance to define routes and handlers
app = FastAPI()

# Create all the tables in the database based on the models
models.Base.metadata.create_all(bind=engine)

# Set up the password hashing scheme using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define the OAuth2 bearer scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Constants for JWT token creation
SECRET_KEY = "mateo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define the base model for User-related data (request/response body for registration)
class UserBase(BaseModel):
    username: str
    password: str

# Define the base model for Post-related data (request/response body for posts)
class PostBase(BaseModel):
    username: str
    user_id: int
    image_url: str
    description: str
    likes: int

# Define the base model for Story-related data (request/response body for stories)
class StoryBase(BaseModel):
    image_url: str
    username: str

# Model for updating a user's information
class UserUpdate(BaseModel):
    username: str
    password: str

# Model for updating a post
class PostUpdate(BaseModel):
    username: str
    user_id: int
    image_url: str
    description: str
    likes: int

# Model for updating a story
class StoryUpdate(BaseModel):
    image_url: str
    hashed_password: str

# Dependency to get a database session, ensures proper closing after use
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CORS settings for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for DB access used in route functions
db_dependency = Annotated[Session, Depends(get_db)]

# Helper function to fetch a user by username from the database
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Function to create a new user
def create_user(db: Session, user: UserBase):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    return "complete"

# Function to authenticate a user
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# Function to create a JWT token for authenticated users
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(pytz.utc) + expires_delta
    else:
        expire = datetime.now(pytz.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify a token
@app.get("/verify-token/")
async def verify_user_token(token: str = Depends(oauth2_scheme)):
    # This function checks if the token is valid and returns appropriate responses
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        return {"message": "Token is valid"}
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")


# Create Endpoints (POST)
@app.post("/register/")
async def register_user(user: UserBase, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)

@app.post("/token/")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()

@app.post("/stories/", status_code=status.HTTP_201_CREATED)
async def create_story(story: StoryBase, db: db_dependency):
    db_story = models.Story(
        username=story.username,
        image_url=story.image_url
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

# Read Endpoints (GET)
@app.get("/posts/", status_code=status.HTTP_200_OK)
async def get_all_posts(db: db_dependency):
    posts = db.query(models.Post).all()
    return posts

@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/users/", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency):
    users = db.query(models.User).all()
    return users

@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/stories/", status_code=status.HTTP_200_OK)
async def get_all_stories(db: db_dependency):
    stories = db.query(models.Story).all()
    return stories

@app.get("/stories/{story_id}", status_code=status.HTTP_200_OK)
async def read_story(story_id: int, db: db_dependency):
    story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@app.get("/verify-token/{token}")
async def verify_user_token(token: str):
    verify_token(token=token)
    return {"message": "Token is valid"}

# Update Endpoints (PUT)
@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(post_id: int, post_update: PostUpdate, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post_update.dict().items():
        setattr(db_post, key, value)
    db.commit()
    return db_post

@app.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_update: UserUpdate, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.dict().items():
        setattr(db_user, key, value)
    db.commit()
    return db_user

@app.put("/stories/{story_id}", status_code=status.HTTP_200_OK)
async def update_story(story_id: int, story_update: StoryUpdate, db: db_dependency):
    db_story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    for key, value in story_update.dict().items():
        setattr(db_story, key, value)
    db.commit()
    return db_story

# Delete Endpoints (DELETE)
@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()

@app.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}

@app.delete("/stories/{story_id}", status_code=status.HTTP_200_OK)
async def delete_story(story_id: int, db: db_dependency):
    db_story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    db.delete(db_story)
    db.commit()
    return {"detail": "Story deleted successfully"}
