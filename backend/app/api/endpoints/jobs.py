from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.document import DocumentType, Job as JobModel
from app.schemas.document import (
    Job as JobSchema, 
    JobDetail, 
    JobUpdate, 
    FileUploadResponse
)
from app.services.document_service import (
    create_document, 
    process_document, 
    get_job, 
    get_jobs_by_user, 
    update_job,
    get_document
)
from app.services.user_service import get_current_user, check_if_company

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_company)  # 只有企业用户可以上传职位
) -> Any:
    """
    上传职位文件
    """
    # 创建文档
    document = await create_document(
        db=db, 
        file=file, 
        user_id=current_user.id,
        document_type=DocumentType.JOB
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


@router.get("/", response_model=List[JobSchema])
async def read_jobs(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    company_name: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取职位列表
    """
    # 如果是企业用户，则只能查看自己发布的职位
    if current_user.role == UserRole.COMPANY:
        jobs = await get_jobs_by_user(db=db, user_id=current_user.id)
        
        # 应用过滤条件（如果提供）
        if is_active is not None:
            jobs = [job for job in jobs if job.is_active == is_active]
        
        return jobs
    
    # 获取所有活跃职位
    query = db.query(JobModel)
    
    if is_active is not None:
        query = query.filter(JobModel.is_active == is_active)
    else:
        # 默认只显示活跃职位
        query = query.filter(JobModel.is_active == True)
    
    # 应用其他过滤条件
    if company_name:
        query = query.filter(JobModel.company_name.ilike(f"%{company_name}%"))
    
    if location:
        query = query.filter(JobModel.location.ilike(f"%{location}%"))
    
    if job_type:
        query = query.filter(JobModel.job_type == job_type)
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobDetail)
async def read_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取指定职位的详细信息
    """
    # 获取职位
    job = await get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 验证是否为活跃职位或者用户是管理员/发布者
    if (not job.is_active and 
        current_user.role != UserRole.ADMIN and 
        job.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="职位不存在或已下线")
    
    # 获取文档
    document = await get_document(db=db, document_id=job.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 构建响应
    job_detail = JobDetail(
        **job.__dict__,
        document=document,
        full_text=document.original_text
    )
    
    return job_detail


@router.put("/{job_id}", response_model=JobSchema)
async def update_job_api(
    job_id: int,
    job_in: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新职位信息
    """
    # 获取职位
    job = await get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 验证权限
    if current_user.role != UserRole.ADMIN and job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此职位"
        )
    
    # 验证用户角色
    if current_user.role != UserRole.ADMIN and current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业用户可以更新职位"
        )
    
    # 更新职位
    updated_job = await update_job(
        db=db, 
        job_id=job_id, 
        update_data=job_in.dict(exclude_unset=True)
    )
    
    return updated_job


@router.post("/{job_id}/toggle-active", response_model=JobSchema)
async def toggle_job_active(
    job_id: int,
    is_active: bool = Query(..., description="设置职位是否处于活跃状态"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    切换职位的活跃状态
    """
    # 获取职位
    job = await get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    # 验证权限
    if current_user.role != UserRole.ADMIN and job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此职位"
        )
    
    # 验证用户角色
    if current_user.role != UserRole.ADMIN and current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业用户可以更新职位"
        )
    
    # 更新职位状态
    updated_job = await update_job(
        db=db, 
        job_id=job_id, 
        update_data={"is_active": is_active}
    )
    
    return updated_job 