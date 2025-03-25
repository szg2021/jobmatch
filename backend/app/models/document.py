from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.sql import func

from app.db.session import Base


class DocumentType(str, Enum):
    RESUME = "resume"
    JOB = "job"


class ProcessStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """文档基本信息，存储在传统数据库中"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    content_type = Column(String)
    file_size = Column(Integer)  # 文件大小（字节）
    original_text = Column(Text)  # 原始文本内容
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    process_status = Column(SQLEnum(ProcessStatus), default=ProcessStatus.PENDING)
    vector_id = Column(String, index=True)  # 向量存储中的ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Resume(Base):
    """简历信息，存储在传统数据库中的关键信息"""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String, index=True)
    name = Column(String, index=True)
    contact = Column(String)  # 联系方式（脱敏存储）
    skills = Column(String)  # 技能，以逗号分隔
    experience = Column(String)  # 工作经验摘要
    education = Column(String)  # 教育背景摘要
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Job(Base):
    """工作岗位信息，存储在传统数据库中的关键信息"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String, index=True)
    company_name = Column(String, index=True)
    location = Column(String, index=True)
    job_type = Column(String, index=True)  # 全职/兼职/实习等
    salary_range = Column(String)
    requirements = Column(Text)
    responsibilities = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)  # 岗位是否处于激活状态 