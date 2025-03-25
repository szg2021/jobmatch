from typing import Any, Dict, List, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.document import Job, Resume, Document, DocumentType
from app.services.document_service import get_job, get_resume, get_document
from app.services.recommendation_service import get_recommended_resumes, get_recommended_jobs, weaviate_client
from app.services.user_service import get_current_user, check_if_company
from app.core.rate_limit import limiter
from app.api.deps import get_current_user, get_db
from app.crud.crud_resume import resume as crud_resume
from app.crud.crud_job import job as crud_job
from app.schemas.recommendation import (
    JobRecommendationResponse,
    ResumeRecommendationResponse
)
from app.schemas.response import StandardResponse
from app.services.feedback_service import feedback_service, FeedbackType
from app.models.feedback import RecommendationFeedback

# 获取日志记录器
logger = logging.getLogger("app.api.recommendations")

router = APIRouter()


class RecommendationResponse(BaseModel):
    id: int
    title: str
    match_score: float
    algorithms: List[str] = []
    match_details: Optional[dict] = None


class JobRecommendation(RecommendationResponse):
    company: Optional[str] = None


class ResumeRecommendation(RecommendationResponse):
    user: dict


class FeedbackRequest(BaseModel):
    feedback_type: str
    job_id: Optional[int] = None
    resume_id: Optional[int] = None
    rating: Optional[float] = None
    comment: Optional[str] = None
    algorithm: Optional[str] = None


@router.get("/jobs", response_model=StandardResponse[List[JobRecommendationResponse]])
async def get_job_recommendations(
    resume_id: int,
    limit: int = 20,
    include_details: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取基于简历的职位推荐
    """
    try:
        # 验证简历所有者
        resume = crud_resume.get(db, id=resume_id)
        if not resume:
            return StandardResponse(
                success=False,
                message="简历不存在",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if resume.user_id != current_user.id:
            return StandardResponse(
                success=False,
                message="您无权访问此简历",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # 获取推荐结果
        recommendations = await get_recommended_jobs(db, resume_id, limit, include_details)
        
        # 返回结果
        return StandardResponse(
            success=True,
            message=f"成功获取{len(recommendations)}个职位推荐",
            data=recommendations
        )
    
    except Exception as e:
        logger.error(f"获取职位推荐时出错: {str(e)}", exc_info=True)
        return StandardResponse(
            success=False,
            message=f"获取推荐失败: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/resumes", response_model=StandardResponse[List[ResumeRecommendationResponse]])
async def get_resume_recommendations(
    job_id: int,
    limit: int = 20,
    include_details: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取基于职位的简历推荐
    """
    try:
        # 验证职位是否存在
        job = crud_job.get(db, id=job_id)
        if not job:
            return StandardResponse(
                success=False,
                message="职位不存在",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 公司用户只能查看自己公司的职位推荐
        if current_user.role == "company" and job.company_id != current_user.company_id:
            return StandardResponse(
                success=False,
                message="您无权访问此职位的推荐",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # 获取推荐结果
        recommendations = await get_recommended_resumes(db, job_id, limit, include_details)
        
        # 返回结果
        return StandardResponse(
            success=True,
            message=f"成功获取{len(recommendations)}个简历推荐",
            data=recommendations
        )
    
    except Exception as e:
        logger.error(f"获取简历推荐时出错: {str(e)}", exc_info=True)
        return StandardResponse(
            success=False,
            message=f"获取推荐失败: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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


@router.get("/system-status", response_model=StandardResponse)
async def get_recommendation_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取推荐系统状态信息
    """
    from app.core.tasks import vector_search_initialized, last_trained_time, training_in_progress
    
    try:
        # 获取系统状态
        status_info = {
            "vector_search_initialized": vector_search_initialized,
            "last_model_training": last_trained_time.isoformat() if last_trained_time else None,
            "training_in_progress": training_in_progress
        }
        
        # 获取数据统计
        from sqlalchemy import func
        job_count = db.query(func.count()).select_from(crud_job.model).scalar()
        resume_count = db.query(func.count()).select_from(crud_resume.model).scalar()
        
        status_info["stats"] = {
            "total_jobs": job_count,
            "total_resumes": resume_count
        }
        
        # 返回结果
        return StandardResponse(
            success=True,
            message="推荐系统状态获取成功",
            data=status_info
        )
    
    except Exception as e:
        logger.error(f"获取推荐系统状态时出错: {str(e)}", exc_info=True)
        return StandardResponse(
            success=False,
            message=f"获取推荐系统状态失败: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/jobs/{resume_id}", response_model=List[JobRecommendation])
async def get_recommended_jobs_for_resume(
    resume_id: int = Path(..., description="简历ID"),
    limit: int = Query(10, description="返回结果数量限制"),
    details: bool = Query(True, description="是否包含匹配详情"),
    use_cache: bool = Query(True, description="是否使用缓存"),
    apply_feedback: bool = Query(True, description="是否应用用户反馈进行个性化"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取针对指定简历的推荐职位列表
    """
    # 检查简历是否属于当前用户
    # 注意：在实际生产环境中应添加适当的权限检查
    
    # 获取推荐职位
    recommendations = await get_recommended_jobs(
        db=db, 
        resume_id=resume_id, 
        limit=limit, 
        include_details=details,
        use_cache=use_cache
    )
    
    # 如果启用了反馈调整且有当前用户
    if apply_feedback and current_user:
        recommendations = await feedback_service.apply_feedback_to_recommendations(
            user_id=current_user.id,
            recommendations=recommendations,
            is_job_recommendations=True
        )
    
    # 记录查看反馈
    if current_user:
        try:
            # 对于每个推荐都记录"已查看"反馈
            for rec in recommendations:
                await feedback_service.record_feedback(
                    db=db,
                    user_id=current_user.id,
                    feedback_type=FeedbackType.VIEWED.value,
                    job_id=rec.get("id"),
                    resume_id=resume_id,
                    algorithm=",".join(rec.get("algorithms", ["unknown"]))
                )
        except Exception as e:
            # 记录错误但不中断响应
            print(f"记录查看反馈时出错: {str(e)}")
    
    return recommendations


@router.get("/resumes/{job_id}", response_model=List[ResumeRecommendation])
async def get_recommended_resumes_for_job(
    job_id: int = Path(..., description="职位ID"),
    limit: int = Query(10, description="返回结果数量限制"),
    details: bool = Query(True, description="是否包含匹配详情"),
    use_cache: bool = Query(True, description="是否使用缓存"),
    apply_feedback: bool = Query(True, description="是否应用用户反馈进行个性化"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取针对指定职位的推荐简历列表
    """
    # 检查职位是否属于当前用户
    # 注意：在实际生产环境中应添加适当的权限检查
    
    # 获取推荐简历
    recommendations = await get_recommended_resumes(
        db=db, 
        job_id=job_id, 
        limit=limit, 
        include_details=details,
        use_cache=use_cache
    )
    
    # 如果启用了反馈调整且有当前用户
    if apply_feedback and current_user:
        recommendations = await feedback_service.apply_feedback_to_recommendations(
            user_id=current_user.id,
            recommendations=recommendations,
            is_job_recommendations=False
        )
    
    # 记录查看反馈
    if current_user:
        try:
            # 对于每个推荐都记录"已查看"反馈
            for rec in recommendations:
                await feedback_service.record_feedback(
                    db=db,
                    user_id=current_user.id,
                    feedback_type=FeedbackType.VIEWED.value,
                    job_id=job_id,
                    resume_id=rec.get("id"),
                    algorithm=",".join(rec.get("algorithms", ["unknown"]))
                )
        except Exception as e:
            # 记录错误但不中断响应
            print(f"记录查看反馈时出错: {str(e)}")
    
    return recommendations


@router.post("/feedback", response_model=dict)
async def submit_recommendation_feedback(
    feedback: FeedbackRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交推荐结果反馈
    """
    if not feedback.job_id and not feedback.resume_id:
        raise HTTPException(status_code=400, detail="必须提供职位ID或简历ID")
    
    try:
        # 记录反馈
        record = await feedback_service.record_feedback(
            db=db,
            user_id=current_user.id,
            feedback_type=feedback.feedback_type,
            job_id=feedback.job_id,
            resume_id=feedback.resume_id,
            rating=feedback.rating,
            comment=feedback.comment,
            algorithm=feedback.algorithm
        )
        
        return {
            "status": "success",
            "message": "反馈已记录",
            "feedback_id": record.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录反馈时出错: {str(e)}")


@router.get("/feedback/user/{user_id}", response_model=List[dict])
async def get_user_feedback(
    user_id: int = Path(..., description="用户ID"),
    feedback_type: Optional[str] = Query(None, description="反馈类型"),
    days: Optional[int] = Query(30, description="查询天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户反馈历史
    """
    # 权限检查：只允许用户查看自己的反馈或管理员查看任何人的反馈
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有权限查看此用户的反馈")
    
    feedbacks = await feedback_service.get_feedback_for_user(
        db=db,
        user_id=user_id,
        feedback_type=feedback_type,
        days=days
    )
    
    # 转换为可序列化格式
    result = []
    for f in feedbacks:
        result.append({
            "id": f.id,
            "user_id": f.user_id,
            "job_id": f.job_id,
            "resume_id": f.resume_id,
            "feedback_type": f.feedback_type,
            "rating": f.rating,
            "comment": f.comment,
            "algorithm": f.algorithm,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })
    
    return result


@router.get("/metrics", response_model=dict)
async def get_recommendation_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    获取推荐系统性能指标（仅管理员可用）
    """
    metrics = await feedback_service.compute_feedback_metrics(db)
    return metrics 