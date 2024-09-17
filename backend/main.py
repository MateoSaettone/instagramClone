# Import necessary modules and libraries for building the API
from fastapi import FastAPI, HTTPException, Depends, status  # FastAPI is the main framework, HTTPException is used for raising HTTP errors, Depends for dependency injection, status for HTTP status codes
from pydantic import BaseModel  # Pydantic's BaseModel is used to define data models for request and response bodies
from typing import Annotated  # Annotated allows for using Python type hints for dependency injection
import models  # Custom module containing the database models
from database import SessionLocal, engine  # SessionLocal handles the DB session, engine connects to the DB
from sqlalchemy.orm import Session  # Session class from SQLAlchemy for interacting with the database
from fastapi.middleware.cors import CORSMiddleware  # Handles Cross-Origin Resource Sharing (CORS) for frontend-backend communication
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # OAuth2PasswordBearer for token authentication, OAuth2PasswordRequestForm for login requests
from jose import JWTError, jwt  # JWTError for handling JWT errors, jwt for creating and decoding tokens
from datetime import datetime, timedelta, timezone  # datetime and timedelta are used to manage dates and times, timezone for time zone handling
from passlib.context import CryptContext  # CryptContext helps to manage password hashing and verification
from models import User  # Import the User model
import pytz  # Pytz handles time zone conversion

# Commands to activate virtual environment and run the FastAPI application (you might already know this)
# .\env\Scripts\Activate
# uvicorn main:app --reload  # Starts the server in reload mode
# source env/bin/activate  # On mac/Linux

# Create a FastAPI instance to define routes and handlers
app = FastAPI()

# Create all the tables in the database based on the models
models.Base.metadata.create_all(bind=engine)

# Set up the password hashing scheme using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define the OAuth2 bearer scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Constants for JWT token creation
SECRET_KEY = "mateo"  # Secret key used for signing the JWT tokens
ALGORITHM = "HS256"  # Algorithm used to sign the JWT token
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiry time in minutes

# Define the base model for User-related data (request/response body for registration)
class UserBase(BaseModel):
    username: str  # Username field
    password: str  # Password field (plaintext, hashed later)

# Define the base model for Post-related data (request/response body for posts)
class PostBase(BaseModel):
    username: str  # Username field
    user_id: int  # User ID field
    image_url: str  # URL of the post's image
    description: str  # Description of the post
    likes: int  # Number of likes for the post

# Define the base model for Story-related data (request/response body for stories)
class StoryBase(BaseModel):
    image_url: str  # URL of the story's image
    username: str  # Username field

# Model for updating a user's information
class UserUpdate(BaseModel):
    username: str  # New username
    password: str  # New password (plaintext)

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
    hashed_password: str  # This field seems unrelated to the story model, but if needed for some reason

# Dependency to get a database session, ensures proper closing after use
def get_db():
    db = SessionLocal()
    try:
        yield db  # Provide the session to be used
    finally:
        db.close()  # Close the session once done

# CORS settings for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from the frontend running on localhost:3000
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Dependency for DB access used in route functions
db_dependency = Annotated[Session, Depends(get_db)]

# Helper function to fetch a user by username from the database
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Function to create a new user, hashes the password before saving to the database
def create_user(db: Session, user: UserBase):
    hashed_password = pwd_context.hash(user.password)  # Hash the plain-text password
    db_user = User(username=user.username, hashed_password=hashed_password)  # Save hashed password
    db.add(db_user)  # Add new user to the DB session
    db.commit()  # Commit changes to the database
    return "complete"

# Function to authenticate a user, checks the hashed password against the stored hash
def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):  # Verify the password against the hash
        return False
    return user

# Function to create a JWT token for authenticated users
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()  # Copy the data (usually username) to be included in the JWT token
    if expires_delta:
        expire = datetime.now(pytz.utc) + expires_delta  # Token expiry time
    else:
        expire = datetime.now(pytz.utc) + timedelta(minutes=15)  # Default 15-minute expiry
    to_encode.update({"exp": expire})  # Add expiry to the token payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode the JWT
    return encoded_jwt

# Function to verify a token
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode the JWT token
        username: str = payload.get("sub")  # Get the username from the token payload
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")

# Route to verify if a token is valid
@app.get("/verify-token/{token}")
async def verify_user_token(token: str):
    verify_token(token=token)  # Call the token verification function
    return {"message": "Token is valid"}

# Route to register a new user
@app.post("/register/")
async def register_user(user: UserBase, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)  # Create the user if not already registered

# Route to log in and get a token (OAuth2 login)
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

# Route to get all posts
@app.get("/posts/", status_code=status.HTTP_200_OK)
async def get_all_posts(db: db_dependency):
    posts = db.query(models.Post).all()
    return posts

# Route to create a new post
@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_dependency):
    db_post = models.Post(**post.dict())  # Convert post data to a dictionary and insert it
    db.add(db_post)
    db.commit()

# Route to get a post by ID
@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Route to update a post by ID
@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(post_id: int, post_update: PostUpdate, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post_update.dict().items():  # Update each field in the post
        setattr(db_post, key, value)
    db.commit()
    return db_post

# Route to delete a post by ID
@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()

# Route to get all users
@app.get("/users/", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency):
    users = db.query(models.User).all()
    return users

# Route to get a user by ID
@app.get("/users/{users_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Route to update a user by ID
@app.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_update: UserUpdate, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.dict().items():  # Update each field in the user
        setattr(db_user, key, value)
    db.commit()
    return db_user

# Route to delete a user by ID
@app.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}

# Route to get all stories
@app.get("/stories/", status_code=status.HTTP_200_OK)
async def get_all_stories(db: db_dependency):
    stories = db.query(models.Story).all()
    return stories

# Route to get a story by ID
@app.get("/stories/{story_id}", status_code=status.HTTP_200_OK)
async def read_story(story_id: int, db: db_dependency):
    story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

# Route to update a story by ID
@app.put("/stories/{story_id}", status_code=status.HTTP_200_OK)
async def update_story(story_id: int, story_update: StoryUpdate, db: db_dependency):
    db_story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    for key, value in story_update.dict().items():  # Update each field in the story
        setattr(db_story, key, value)
    db.commit()
    return db_story

# Route to delete a story by ID
@app.delete("/stories/{story_id}", status_code=status.HTTP_200_OK)
async def delete_story(story_id: int, db: db_dependency):
    db_story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    db.delete(db_story)
    db.commit()
    return {"detail": "Story deleted successfully"}
