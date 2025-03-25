from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.user import CompanyProfile, CompanyProfileCreate, CompanyProfileUpdate
from app.schemas.user import JobSeekerProfile, JobSeekerProfileCreate, JobSeekerProfileUpdate
from app.services.user_service import (
    get_user, get_company_profile, get_jobseeker_profile,
    create_user, update_user, get_current_user, check_if_admin
)

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_admin)
) -> Any:
    """
    获取所有用户列表（仅管理员）
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=UserSchema)
async def create_user_api(
    user_in: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_admin)
) -> Any:
    """
    创建用户（仅管理员）
    """
    return create_user(db=db, user_in=user_in)


@router.get("/{user_id}", response_model=UserSchema)
async def read_user_by_id(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取指定用户信息
    """
    # 管理员可以查看任何用户，普通用户只能查看自己
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看其他用户信息"
        )
    
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user_api(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新用户信息
    """
    # 管理员可以更新任何用户，普通用户只能更新自己
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新其他用户信息"
        )
    
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 如果普通用户尝试修改自己的角色，则阻止
    if current_user.role != UserRole.ADMIN and user_in.role != user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改用户角色"
        )
    
    return update_user(db=db, user_id=user_id, user_in=user_in)


@router.get("/{user_id}/company-profile", response_model=CompanyProfile)
async def read_company_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取用户的企业资料
    """
    # 管理员可以查看任何用户的企业资料，普通用户只能查看自己的
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看其他用户的企业资料"
        )
    
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    if user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=400,
            detail="该用户不是企业用户"
        )
    
    profile = get_company_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="企业资料不存在"
        )
    
    return profile


@router.put("/{user_id}/company-profile", response_model=CompanyProfile)
async def update_company_profile(
    user_id: int,
    profile_in: CompanyProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新用户的企业资料
    """
    # 管理员可以更新任何用户的企业资料，普通用户只能更新自己的
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新其他用户的企业资料"
        )
    
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    if user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=400,
            detail="该用户不是企业用户"
        )
    
    profile = get_company_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="企业资料不存在"
        )
    
    # 更新资料
    update_data = profile_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/{user_id}/jobseeker-profile", response_model=JobSeekerProfile)
async def read_jobseeker_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取用户的求职者资料
    """
    # 管理员可以查看任何用户的求职者资料，普通用户只能查看自己的
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看其他用户的求职者资料"
        )
    
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    if user.role != UserRole.JOBSEEKER:
        raise HTTPException(
            status_code=400,
            detail="该用户不是求职者"
        )
    
    profile = get_jobseeker_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="求职者资料不存在"
        )
    
    return profile


@router.put("/{user_id}/jobseeker-profile", response_model=JobSeekerProfile)
async def update_jobseeker_profile(
    user_id: int,
    profile_in: JobSeekerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新用户的求职者资料
    """
    # 管理员可以更新任何用户的求职者资料，普通用户只能更新自己的
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新其他用户的求职者资料"
        )
    
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    if user.role != UserRole.JOBSEEKER:
        raise HTTPException(
            status_code=400,
            detail="该用户不是求职者"
        )
    
    profile = get_jobseeker_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="求职者资料不存在"
        )
    
    # 更新资料
    update_data = profile_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile 