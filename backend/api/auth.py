from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
from db.postgres_client import create_user, get_user_by_identifier
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class UserSignup(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    login_id: str  # Can be email or username
    password: str

@router.post("/auth/signup")
def signup(user: UserSignup):
    # Check if email or username already exists
    existing_user = get_user_by_identifier(user.email)
    if existing_user:
        if existing_user['email'] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            raise HTTPException(status_code=400, detail="Username already taken")
            
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    hashed_password_str = hashed_password.decode('utf-8')
    
    new_user = create_user(user.username, user.email, hashed_password_str)
    return {"message": "User created successfully", "user_id": new_user["id"]}

@router.post("/auth/login")
def login(user: UserLogin):
    db_user = get_user_by_identifier(user.login_id)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials. Access denied.")
    
    hashed_password_str = db_user['hashed_password']
    if not bcrypt.checkpw(user.password.encode('utf-8'), hashed_password_str.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials. Access denied.")
        
    return {"token": f"mock_token_{db_user['id']}", "user_id": str(db_user['id'])}