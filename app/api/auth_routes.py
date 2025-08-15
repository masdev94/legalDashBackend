from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.auth import UserCreate, UserLogin, UserResponse, Token, PasswordChange, UserUpdate
from app.services.auth_service import AuthService
from loguru import logger

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
auth_service = AuthService()

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    try:
        user = auth_service.create_user(user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        return user
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin):
    try:
        user = auth_service.authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        access_token = auth_service.create_access_token(
            data={"sub": user["email"], "user_id": user["id"], "role": user["role"]}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                full_name=user["full_name"],
                role=user["role"],
                created_at=user["created_at"],
                last_login=user["last_login"]
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            created_at=user["created_at"],
            last_login=user["last_login"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        current_user = auth_service.get_current_user(credentials.credentials)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        if user_update.full_name:
            current_user["full_name"] = user_update.full_name
        
        if user_update.role and current_user["role"] == "admin":
            current_user["role"] = user_update.role
        
        auth_service.mock_users[current_user["email"]] = current_user
        
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=current_user["full_name"],
            role=current_user["role"],
            created_at=current_user["created_at"],
            last_login=current_user["last_login"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        current_user = auth_service.get_current_user(credentials.credentials)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        if not auth_service.verify_password(password_change.current_password, current_user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        new_hashed_password = auth_service.get_password_hash(password_change.new_password)
        current_user["hashed_password"] = new_hashed_password
        auth_service.mock_users[current_user["email"]] = current_user
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@router.get("/users", response_model=list[UserResponse])
async def get_all_users(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        current_user = auth_service.get_current_user(credentials.credentials)
        if not current_user or current_user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        users = []
        for user_data in auth_service.mock_users.values():
            users.append(UserResponse(
                id=user_data["id"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                created_at=user_data["created_at"],
                last_login=user_data["last_login"]
            ))
        
        return users
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get all users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )
