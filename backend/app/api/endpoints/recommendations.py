from typing import Any, Dict, List
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.document import Job, Resume, Document, DocumentType
from app.services.document_service import get_job, get_resume, get_document
from app.services.recommendation_service import get_recommended_resumes, get_recommended_jobs, weaviate_client
from app.services.user_service import get_current_user, check_if_company
from app.core.rate_limit import limiter

# 获取日志记录器
logger = logging.getLogger("app.api.recommendations")

router = APIRouter()


@router.get("/jobs-for-resume/{resume_id}", response_model=List[Dict[str, Any]])
@limiter.limit("10/minute")
async def get_jobs_for_resume(
    resume_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取与特定简历匹配的岗位推荐
    """
    # 验证简历是否存在
    resume = await get_resume(db=db, resume_id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    # 验证权限
    if current_user.role != UserRole.ADMIN and resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此简历的推荐"
        )
    
    # 验证用户角色
    if current_user.role != UserRole.JOBSEEKER and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有求职者可以获取岗位推荐"
        )
    
    # 获取推荐岗位
    recommended_jobs = await get_recommended_jobs(db=db, resume_id=resume_id, limit=limit)
    return recommended_jobs


@router.get("/resumes-for-job/{job_id}", response_model=List[Dict[str, Any]])
@limiter.limit("10/minute")
async def get_resumes_for_job(
    job_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取与特定岗位匹配的简历推荐
    """
    # 验证岗位是否存在
    job = await get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    
    # 验证权限
    if current_user.role != UserRole.ADMIN and job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此岗位的推荐"
        )
    
    # 验证用户角色
    if current_user.role != UserRole.COMPANY and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业用户可以获取人才推荐"
        )
    
    # 获取推荐简历
    recommended_resumes = await get_recommended_resumes(db=db, job_id=job_id, limit=limit)
    return recommended_resumes


@router.get("/top-matches-for-jobseeker", response_model=List[Dict[str, Any]])
@limiter.limit("5/minute")
async def get_top_matches_for_jobseeker(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前求职者的顶级职位匹配推荐
    """
    # 验证用户角色
    if current_user.role != UserRole.JOBSEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有求职者可以使用此功能"
        )
    
    # 获取用户的所有简历
    user_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    if not user_resumes:
        return []
    
    # 使用用户的第一份简历获取推荐
    # 实际应用中可能需要更复杂的逻辑，例如选择最新上传的简历或让用户选择
    primary_resume = user_resumes[0]
    recommended_jobs = await get_recommended_jobs(db=db, resume_id=primary_resume.id, limit=limit)
    
    return recommended_jobs


@router.get("/top-matches-for-company", response_model=List[Dict[str, Any]])
@limiter.limit("5/minute")
async def get_top_matches_for_company(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_company)
) -> Any:
    """
    获取当前企业的顶级人才匹配推荐
    """
    # 获取企业发布的所有岗位
    company_jobs = db.query(Job).filter(Job.user_id == current_user.id, Job.is_active == True).all()
    if not company_jobs:
        return []
    
    # 使用第一个岗位获取推荐
    # 实际应用中可能需要更复杂的逻辑，例如选择最新发布的岗位或让用户选择
    primary_job = company_jobs[0]
    recommended_resumes = await get_recommended_resumes(db=db, job_id=primary_job.id, limit=limit)
    
    return recommended_resumes


@router.get("/detailed-match/{resume_id}/{job_id}", response_model=Dict[str, Any])
@limiter.limit("20/minute")
async def get_detailed_match(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取指定简历和岗位之间的详细匹配信息
    """
    try:
        # 验证简历是否存在
        resume = await get_resume(db=db, resume_id=resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 验证岗位是否存在
        job = await get_job(db=db, job_id=job_id)
        if not job:
            raise HTTPException(status_code=404, detail="岗位不存在")
        
        # 验证权限
        has_resume_access = current_user.role == UserRole.ADMIN or resume.user_id == current_user.id
        has_job_access = current_user.role == UserRole.ADMIN or (job.user_id == current_user.id and job.is_active)
        
        # 求职者可以查看自己的简历与任何岗位的匹配
        # 企业可以查看自己的岗位与任何简历的匹配
        if not (has_resume_access or has_job_access):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此匹配信息"
            )
        
        # 获取简历文档
        resume_document = await get_document(db=db, document_id=resume.document_id)
        if not resume_document:
            raise HTTPException(status_code=404, detail="简历文档不存在")
        
        # 获取岗位文档
        job_document = await get_document(db=db, document_id=job.document_id)
        if not job_document:
            raise HTTPException(status_code=404, detail="岗位文档不存在")
        
        # 计算匹配分数和原因（这里简化实现，实际中可能调用外部服务）
        # 在真实应用中，会使用一个专门的匹配服务来比较简历和岗位
        
        match_details = {
            "resume": {
                "id": resume.id,
                "title": resume.title,
                "skills": resume.skills.split(",") if resume.skills else []
            },
            "job": {
                "id": job.id,
                "title": job.title,
                "company_name": job.company_name,
                "requirements": job.requirements.split("\n") if job.requirements else []
            },
            "match": {
                "score": 0.0,
                "matching_skills": [],
                "missing_skills": [],
                "highlights": []
            }
        }
        
        # 简化的匹配实现
        # 在实际应用中，可以使用LLM或专门的匹配算法进行更深入的分析
        job_skills = []
        resume_skills = []
        
        try:
            if job.requirements:
                job_skills = [req.strip().lower() for req in job.requirements.split("\n") if req.strip()]
            
            if resume.skills:
                resume_skills = [skill.strip().lower() for skill in resume.skills.split(",") if skill.strip()]
            
            # 计算匹配的技能
            if job_skills and resume_skills:
                matching_skills = set(job_skills).intersection(set(resume_skills))
                missing_skills = set(job_skills) - set(resume_skills)
                
                match_details["match"]["matching_skills"] = list(matching_skills)
                match_details["match"]["missing_skills"] = list(missing_skills)
                
                # 简单计算匹配分数
                if job_skills:
                    match_details["match"]["score"] = len(matching_skills) / len(job_skills)
        except Exception as e:
            # 处理技能匹配计算中的错误
            logger.error(f"计算技能匹配时出错: {str(e)}")
            # 不要中断API请求，使用默认值继续
        
        return match_details
        
    except HTTPException:
        # 直接重新抛出HTTP异常
        raise
    except Exception as e:
        # 捕获其他所有异常
        logger.error(f"处理详细匹配请求时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理匹配请求时发生错误"
        )


@router.get("/stats", response_model=Dict[str, Any])
@limiter.limit("30/minute")
async def get_recommendation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取推荐系统的统计信息
    """
    # 根据用户角色返回不同的统计信息
    stats = {
        "total": {
            "resumes": db.query(Resume).count(),
            "jobs": db.query(Job).filter(Job.is_active == True).count(),
        }
    }
    
    if current_user.role == UserRole.ADMIN:
        # 管理员可以看到所有统计
        stats["system"] = {
            "total_matches_processed": db.query(Resume).filter(Resume.id > 0).count() * db.query(Job).filter(Job.is_active == True).count(),
            "indexed_resumes": db.query(Document).filter(Document.document_type == DocumentType.RESUME, Document.vector_id != None).count(),
            "indexed_jobs": db.query(Document).filter(Document.document_type == DocumentType.JOB, Document.vector_id != None).count()
        }
    
    elif current_user.role == UserRole.JOBSEEKER:
        # 求职者统计
        user_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
        stats["user"] = {
            "resumes": user_resumes,
            "potential_matches": user_resumes * stats["total"]["jobs"] if user_resumes > 0 else 0
        }
    
    elif current_user.role == UserRole.COMPANY:
        # 企业统计
        active_jobs = db.query(Job).filter(Job.user_id == current_user.id, Job.is_active == True).count()
        stats["company"] = {
            "active_jobs": active_jobs,
            "potential_candidates": active_jobs * stats["total"]["resumes"] if active_jobs > 0 else 0
        }
    
    return stats 