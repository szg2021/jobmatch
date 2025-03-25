from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.document import DocumentType, ProcessStatus


# 文档基本模式
class DocumentBase(BaseModel):
    filename: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    document_type: DocumentType


# 创建文档时使用的模式
class DocumentCreate(DocumentBase):
    user_id: int
    file_path: str
    original_text: Optional[str] = None


# 更新文档时使用的模式
class DocumentUpdate(BaseModel):
    process_status: Optional[ProcessStatus] = None
    vector_id: Optional[str] = None
    original_text: Optional[str] = None


# 数据库中的文档
class DocumentInDB(DocumentBase):
    id: int
    user_id: int
    file_path: str
    process_status: ProcessStatus
    vector_id: Optional[str] = None
    original_text: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# API响应中的文档
class Document(DocumentInDB):
    class Config:
        from_attributes = True


# 简历基本模式
class ResumeBase(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    contact: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None


# 创建简历时使用的模式
class ResumeCreate(ResumeBase):
    document_id: int
    user_id: int


# 更新简历时使用的模式
class ResumeUpdate(ResumeBase):
    pass


# 数据库中的简历
class ResumeInDB(ResumeBase):
    id: int
    document_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# API响应中的简历
class Resume(ResumeInDB):
    document: Document = None

    class Config:
        from_attributes = True


# 带有所有细节的简历（包括原始文本内容）
class ResumeDetail(Resume):
    full_text: Optional[str] = None  # 从文档中提取的完整文本

    class Config:
        from_attributes = True


# 工作岗位基本模式
class JobBase(BaseModel):
    title: str
    company_name: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    is_active: bool = True


# 创建工作岗位时使用的模式
class JobCreate(JobBase):
    document_id: int
    user_id: int


# 更新工作岗位时使用的模式
class JobUpdate(JobBase):
    pass


# 数据库中的工作岗位
class JobInDB(JobBase):
    id: int
    document_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# API响应中的工作岗位
class Job(JobInDB):
    document: Optional[Document] = None

    class Config:
        from_attributes = True


# 带有所有细节的工作岗位（包括原始文本内容）
class JobDetail(Job):
    full_text: Optional[str] = None  # 从文档中提取的完整文本

    class Config:
        from_attributes = True


# 文件上传响应
class FileUploadResponse(BaseModel):
    filename: str
    document_id: int
    content_type: str
    file_size: int
    status: ProcessStatus 