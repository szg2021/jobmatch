from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


# 基础用户模式
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = UserRole.JOBSEEKER
    is_active: Optional[bool] = True


# 创建用户时使用的模式
class UserCreate(UserBase):
    password: str
    

# 更新用户时使用的模式
class UserUpdate(UserBase):
    password: Optional[str] = None


# 数据库中的用户
class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# API响应中的用户
class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 公司资料基础模式
class CompanyProfileBase(BaseModel):
    company_name: str
    company_description: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None


# 创建公司资料
class CompanyProfileCreate(CompanyProfileBase):
    user_id: int


# 更新公司资料
class CompanyProfileUpdate(CompanyProfileBase):
    pass


# 数据库中的公司资料
class CompanyProfileInDB(CompanyProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# API响应中的公司资料
class CompanyProfile(CompanyProfileInDB):
    class Config:
        from_attributes = True


# 求职者资料基础模式
class JobSeekerProfileBase(BaseModel):
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    education: Optional[str] = None
    experience_years: Optional[int] = None


# 创建求职者资料
class JobSeekerProfileCreate(JobSeekerProfileBase):
    user_id: int


# 更新求职者资料
class JobSeekerProfileUpdate(JobSeekerProfileBase):
    pass


# 数据库中的求职者资料
class JobSeekerProfileInDB(JobSeekerProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# API响应中的求职者资料
class JobSeekerProfile(JobSeekerProfileInDB):
    class Config:
        from_attributes = True 