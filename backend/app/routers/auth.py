"""
Authentication router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import LoginRequest, TokenResponse, UserResponse
from app.auth import login, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login_endpoint(request: LoginRequest):
    """
    Login endpoint
    
    - **username**: Admin1
    - **password**: Admin123
    """
    return login(request.username, request.password)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user


@router.post("/verify", response_model=UserResponse)
async def verify_token(current_user: UserResponse = Depends(get_current_user)):
    """Verify if token is valid"""
    return current_user