from sqlalchemy import Column, Integer, String
from app.db.database import Base
from pydantic import BaseModel, EmailStr

# --- SQLAlchemy 模型 (数据库表结构) ---
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# --- Pydantic 模型 (前端数据验证) ---
class UserRegister(BaseModel):
    nickname: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str # 对应前端传来的 email
    password: str