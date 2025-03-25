from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.document import DocumentType
from app.schemas.document import (
    Resume as ResumeSchema, 
    ResumeDetail, 
    ResumeUpdate, 
    FileUploadResponse
)
from app.services.document_service import (
    create_document, 
    process_document, 
    get_resume, 
    get_resumes_by_user, 
    update_resume,
    get_document
)
from app.services.user_service import get_current_user

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    上传简历文件
    """
    # 验证用户是否为求职者
    if current_user.role != UserRole.JOBSEEKER and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有求职者可以上传简历"
        )
    
    # 创建文档
    document = await create_document(
        db=db, 
        file=file, 
        user_id=current_user.id,
        document_type=DocumentType.RESUME
    )
    
    # 异步处理文档
    background_tasks.add_task(process_document, db=db, document_id=document.id)
    
    return FileUploadResponse(
        filename=document.filename,
        document_id=document.id,
        content_type=document.content_type,
        file_size=document.file_size,
        status=document.process_status
    )


@router.get("/", response_model=List[ResumeSchema])
async def read_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取用户的简历列表
    """
    # 验证用户是否为求职者或管理员
    if current_user.role != UserRole.JOBSEEKER and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有求职者和管理员可以查看简历"
        )
    
    resumes = await get_resumes_by_user(db=db, user_id=current_user.id)
    return resumes


@router.get("/{resume_id}", response_model=ResumeDetail)
async def read_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取指定简历的详细信息
    """
    # 获取简历
    resume = await get_resume(db=db, resume_id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 验证权限
    if current_user.role != UserRole.ADMIN and resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此简历"
        )
    
    # 获取文档
    document = await get_document(db=db, document_id=resume.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 构建响应
    resume_detail = ResumeDetail(
        **resume.__dict__,
        document=document,
        full_text=document.original_text
    )
    
    return resume_detail


@router.put("/{resume_id}", response_model=ResumeSchema)
async def update_resume_api(
    resume_id: int,
    resume_in: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新简历信息
    """
    # 获取简历
    resume = await get_resume(db=db, resume_id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 验证权限
    if current_user.role != UserRole.ADMIN and resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此简历"
        )
    
    # 更新简历
    updated_resume = await update_resume(
        db=db, 
        resume_id=resume_id, 
        update_data=resume_in.dict(exclude_unset=True)
    )
    
    return updated_resume 