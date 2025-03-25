from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, ALGORITHM
from app.db.session import get_db
from app.models.user import User, CompanyProfile, JobSeekerProfile, UserRole
from app.schemas.token import TokenPayload
from app.schemas.user import UserCreate, UserUpdate

# OAuth2 密码Bearer令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


# 获取用户
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


# 通过邮箱获取用户
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


# 通过手机号获取用户
def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    return db.query(User).filter(User.phone == phone).first()


# 通过邮箱或手机号获取用户
def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    # 首先尝试邮箱
    user = get_user_by_email(db, email=identifier)
    if user:
        return user
    
    # 然后尝试手机号
    return get_user_by_phone(db, phone=identifier)


# 创建用户
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    # 检查邮箱是否已存在
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册",
        )
    
    # 检查手机号是否已存在
    if user_in.phone:
        db_user_by_phone = get_user_by_phone(db, phone=user_in.phone)
        if db_user_by_phone:
            raise HTTPException(
                status_code=400,
                detail="该手机号已被注册",
            )
    
    # 创建新用户
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=user_in.role,
        is_active=user_in.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 创建对应的用户资料
    if db_user.role == UserRole.COMPANY:
        company_profile = CompanyProfile(user_id=db_user.id)
        db.add(company_profile)
        db.commit()
    elif db_user.role == UserRole.JOBSEEKER:
        jobseeker_profile = JobSeekerProfile(user_id=db_user.id)
        db.add(jobseeker_profile)
        db.commit()
    
    return db_user


# 更新用户
def update_user(
    db: Session, user_id: int, user_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )
    
    update_data = user_in if isinstance(user_in, dict) else user_in.dict(exclude_unset=True)
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 验证用户
def authenticate_user(email: str, password: str, db: Session = Depends(get_db)) -> Optional[User]:
    # 支持使用邮箱或手机号登录
    user = get_user_by_identifier(db, identifier=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# 从令牌获取当前用户
async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenPayload(sub=email)
    except JWTError:
        raise credentials_exception
    
    # 尝试通过邮箱或手机号获取用户
    user = get_user_by_identifier(db, identifier=token_data.sub)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="账户已停用")
    return user


# 获取当前活跃用户
def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="账户已停用")
    return current_user


# 检查是否为管理员
def check_if_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限",
        )
    return current_user


# 检查是否为企业用户
def check_if_company(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要企业用户权限",
        )
    return current_user


# 获取企业资料
def get_company_profile(db: Session, user_id: int) -> Optional[CompanyProfile]:
    return db.query(CompanyProfile).filter(CompanyProfile.user_id == user_id).first()


# 获取求职者资料
def get_jobseeker_profile(db: Session, user_id: int) -> Optional[JobSeekerProfile]:
    return db.query(JobSeekerProfile).filter(JobSeekerProfile.user_id == user_id).first() 