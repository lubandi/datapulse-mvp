"""Authentication router - IMPLEMENTED."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserCreate, Token, LoginRequest
from app.services.auth_service import create_user, authenticate_user
from app.utils.jwt_handler import create_access_token

router = APIRouter()


@router.post("/register", response_model=Token, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return a JWT token."""
    user = create_user(db, user_data)
    if user is None:
        raise HTTPException(status_code=400, detail="Email already registered")
    token = create_access_token(data={"sub": user.email})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return a JWT token."""
    user = authenticate_user(db, login_data.email, login_data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(data={"sub": user.email})
    return Token(access_token=token)
