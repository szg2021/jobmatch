from enum import Enum
from sqlalchemy import Boolean, Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func

from app.db.session import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    COMPANY = "company"
    JOBSEEKER = "jobseeker"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    phone = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.JOBSEEKER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, unique=True)
    company_name = Column(String, index=True)
    company_description = Column(String)
    industry = Column(String, index=True)
    size = Column(String)
    location = Column(String)
    website = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobSeekerProfile(Base):
    __tablename__ = "jobseeker_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, unique=True)
    birth_date = Column(DateTime)
    gender = Column(String)
    current_position = Column(String)
    current_company = Column(String)
    education = Column(String)
    experience_years = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 