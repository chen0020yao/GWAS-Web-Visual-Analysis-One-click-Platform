from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import os
import shutil
from app.db.database import get_db
from app.models.user import UserDB, UserRegister, UserLogin

router = APIRouter()

AVATAR_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)


def get_current_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """从token中解析当前用户 (简化版)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        token = authorization.replace("Bearer ", "")
        if not token.startswith("token_"):
            raise HTTPException(status_code=401, detail="无效token")
        parts = token.split("_")
        user_id = int(parts[1])
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        return user
    except (IndexError, ValueError):
        raise HTTPException(status_code=401, detail="无效token")


@router.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(
        or_(UserDB.email == user.email, UserDB.nickname == user.nickname)
    ).first()

    if db_user:
        detail = "该邮箱已被注册" if db_user.email == user.email else "该昵称已被占用"
        raise HTTPException(status_code=400, detail=detail)

    new_user = UserDB(
        nickname=user.nickname,
        email=user.email,
        hashed_password=user.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "注册成功", "nickname": new_user.nickname}


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    user_in_db = db.query(UserDB).filter(
        or_(UserDB.email == user.username, UserDB.nickname == user.username)
    ).first()

    if not user_in_db or user_in_db.hashed_password != user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")

    return {
        "access_token": f"token_{user_in_db.id}_{user_in_db.nickname}",
        "token_type": "bearer",
        "nickname": user_in_db.nickname
    }


@router.get("/info")
async def get_user_info(current_user: UserDB = Depends(get_current_user)):
    # 查找用户头像文件
    avatar = None
    if os.path.exists(AVATAR_DIR):
        for f in os.listdir(AVATAR_DIR):
            if f.startswith(str(current_user.id) + "."):
                avatar = f"/api/user/avatar-file/{f}"
                break
    return {
        "id": current_user.id,
        "username": current_user.email,
        "nickname": current_user.nickname,
        "email": current_user.email,
        "avatar": avatar,
        "role": "user",
        "created_at": str(current_user.id)
    }


@router.patch("/update")
async def update_profile(data: dict, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if "nickname" in data and data["nickname"]:
        current_user.nickname = data["nickname"]
    if "email" in data and data["email"]:
        current_user.email = data["email"]
    db.commit()
    db.refresh(current_user)
    return {"message": "更新成功", "nickname": current_user.nickname}


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(None), current_user: UserDB = Depends(get_current_user)):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{current_user.id}{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": "头像上传成功", "avatar": f"/api/user/avatar-file/{filename}"}


@router.post("/logout")
async def logout():
    return {"message": "已退出登录"}


@router.get("/avatar-file/{filename}")
async def get_avatar_file(filename: str):
    from fastapi.responses import FileResponse
    filepath = os.path.join(AVATAR_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="头像不存在")
    return FileResponse(filepath)


@router.post("/password")
async def change_password(data: dict, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    old_pw = data.get("old_password")
    new_pw = data.get("new_password")
    if not old_pw or not new_pw:
        raise HTTPException(status_code=400, detail="请输入新旧密码")
    if current_user.hashed_password != old_pw:
        raise HTTPException(status_code=400, detail="原密码错误")
    current_user.hashed_password = new_pw
    db.commit()
    return {"message": "密码修改成功"}
