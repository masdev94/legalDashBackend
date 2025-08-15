import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from loguru import logger
from app.models.auth import UserCreate, UserResponse, TokenData
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        
        self.mock_users = {
            "admin@legal.com": {
                "id": "admin-001",
                "email": "admin@legal.com",
                "full_name": "Admin User",
                "role": "admin",
                "hashed_password": pwd_context.hash("admin123"),
                "created_at": datetime.now(),
                "last_login": None
            },
            "user@legal.com": {
                "id": "user-001",
                "email": "user@legal.com",
                "full_name": "Regular User",
                "role": "user",
                "hashed_password": pwd_context.hash("user123"),
                "created_at": datetime.now(),
                "last_login": None
            }
        }
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.mock_users.get(email)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        
        user["last_login"] = datetime.now()
        return user
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            role: str = payload.get("role")
            
            if email is None:
                return None
            
            return TokenData(email=email, user_id=user_id, role=role)
        except jwt.PyJWTError:
            return None
    
    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        token_data = self.verify_token(token)
        if token_data is None:
            return None
        
        user = self.mock_users.get(token_data.email)
        return user
    
    def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        if user_data.email in self.mock_users:
            return None
        
        user_id = str(uuid.uuid4())
        hashed_password = self.get_password_hash(user_data.password)
        
        new_user = {
            "id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "role": user_data.role,
            "hashed_password": hashed_password,
            "created_at": datetime.now(),
            "last_login": None
        }
        
        self.mock_users[user_data.email] = new_user
        
        return UserResponse(
            id=new_user["id"],
            email=new_user["email"],
            full_name=new_user["full_name"],
            role=new_user["role"],
            created_at=new_user["created_at"],
            last_login=new_user["last_login"]
        )
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.mock_users.get(email)
    
    def update_user_last_login(self, email: str):
        if email in self.mock_users:
            self.mock_users[email]["last_login"] = datetime.now()
