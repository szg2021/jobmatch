from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db, get_admin_user
from app.models.user import User
from app.schemas.response import StandardResponse
from app.core.tasks import (
    initialize_search_services,
    train_lightfm_model,
    vector_search_initialized,
    last_trained_time,
    training_in_progress
)

import logging
from sqlalchemy import func

logger = logging.getLogger("app.api.admin.recommendation_management")

router = APIRouter()


@router.post("/initialize-vector-search", response_model=StandardResponse)
async def initialize_vector_search(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    初始化向量搜索服务（仅管理员可操作）
    """
    try:
        if vector_search_initialized:
            return StandardResponse(
                success=True,
                message="向量搜索服务已经初始化，无需重新初始化",
            )
        
        success = await initialize_search_services(db)
        
        if success:
            return StandardResponse(
                success=True,
                message="向量搜索服务初始化成功"
            )
        else:
            return StandardResponse(
                success=False,
                message="向量搜索服务初始化失败，请查看日志获取详细信息",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        logger.error(f"手动初始化向量搜索服务时出错: {str(e)}", exc_info=True)
        return StandardResponse(
            success=False,
            message=f"初始化过程中出错: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/train-model", response_model=StandardResponse)
async def trigger_model_training(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    手动触发模型训练（仅管理员可操作）
    """
    try:
        if training_in_progress:
            return StandardResponse(
                success=False,
                message="另一个训练任务正在进行中，请等待完成后再试",
                status_code=status.HTTP_409_CONFLICT
            )
        
        if not vector_search_initialized:
            # 先尝试初始化向量搜索服务
            logger.info("向量搜索服务未初始化，正在尝试初始化...")
            vector_init_success = await initialize_search_services(db)
            if not vector_init_success:
                return StandardResponse(
                    success=False,
                    message="无法初始化向量搜索服务，模型训练失败",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # 启动模型训练
        success = await train_lightfm_model()
        
        if success:
            return StandardResponse(
                success=True,
                message="模型训练任务已成功完成",
                data={"last_trained": last_trained_time.isoformat() if last_trained_time else None}
            )
        else:
            return StandardResponse(
                success=False,
                message="模型训练失败，请查看日志获取详细信息",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    except Exception as e:
        logger.error(f"手动触发模型训练时出错: {str(e)}", exc_info=True)
        return StandardResponse(
            success=False,
            message=f"训练过程中出错: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/recommendation-system-status", response_model=StandardResponse)
async def get_recommendation_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    获取推荐系统详细状态（仅管理员可操作）
    """
    try:
        # 获取系统状态
        status_info = {
            "vector_search_initialized": vector_search_initialized,
            "last_model_training": last_trained_time.isoformat() if last_trained_time else None,
            "training_in_progress": training_in_progress
        }
        
        # 获取数据统计
        from app.crud.crud_job import job as crud_job
        from app.crud.crud_resume import resume as crud_resume
        from sqlalchemy import func
        
        job_count = db.query(func.count()).select_from(crud_job.model).scalar()
        resume_count = db.query(func.count()).select_from(crud_resume.model).scalar()
        
        # 获取配置信息
        from app.crud.crud_recommendation_config import recommendation_config
        active_config = recommendation_config.get_active_config(db)
        
        status_info["stats"] = {
            "total_jobs": job_count,
            "total_resumes": resume_count
        }
        
        if active_config:
            status_info["active_config"] = {
                "id": active_config.id,
                "name": active_config.name,
                "no_components": active_config.no_components,
                "learning_rate": active_config.learning_rate,
                "loss": active_config.loss,
                "vector_search_weight": active_config.vector_search_weight,
                "lightfm_weight": active_config.lightfm_weight,
                "skill_match_weight": active_config.skill_match_weight,
                "train_on_startup": active_config.train_on_startup,
                "train_schedule": active_config.train_schedule,
                "created_at": active_config.created_at.isoformat() if active_config.created_at else None,
                "updated_at": active_config.updated_at.isoformat() if active_config.updated_at else None
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


@router.get("/health-check", response_model=StandardResponse)
async def recommendation_system_health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    检查推荐系统的健康状态

    执行一系列检查以确保推荐系统的各个组件正常运行
    - 检查向量搜索服务
    - 检查LightFM模型状态
    - 验证配置有效性
    - 检查数据库中是否有足够的数据
    """
    try:
        health_status = {
            "vector_search": {
                "status": "unknown",
                "message": "",
                "last_check": datetime.now().isoformat()
            },
            "lightfm": {
                "status": "unknown",
                "message": "",
                "last_check": datetime.now().isoformat()
            },
            "database": {
                "status": "unknown",
                "message": "",
                "last_check": datetime.now().isoformat()
            },
            "configuration": {
                "status": "unknown", 
                "message": "",
                "last_check": datetime.now().isoformat()
            },
            "overall_status": "unknown"
        }
        
        # 检查向量搜索服务
        vector_initialized = False
        try:
            # 检查向量搜索服务是否初始化
            from app.core.tasks import vector_search_initialized
            vector_initialized = vector_search_initialized
            
            if vector_initialized:
                health_status["vector_search"]["status"] = "healthy"
                health_status["vector_search"]["message"] = "向量搜索服务已初始化且正常运行"
            else:
                health_status["vector_search"]["status"] = "warning"
                health_status["vector_search"]["message"] = "向量搜索服务尚未初始化"
        except Exception as e:
            health_status["vector_search"]["status"] = "error"
            health_status["vector_search"]["message"] = f"检查向量搜索服务时出错: {str(e)}"
            logger.error(f"检查向量搜索服务时出错: {str(e)}", exc_info=True)
        
        # 检查LightFM模型
        try:
            from app.services.lightfm_recommendation_service import is_lightfm_ready
            lightfm_ready = is_lightfm_ready()
            
            if lightfm_ready:
                health_status["lightfm"]["status"] = "healthy"
                health_status["lightfm"]["message"] = "LightFM模型已加载且可用"
            else:
                health_status["lightfm"]["status"] = "warning"
                health_status["lightfm"]["message"] = "LightFM模型尚未就绪，可能需要训练"
        except Exception as e:
            health_status["lightfm"]["status"] = "error"
            health_status["lightfm"]["message"] = f"检查LightFM模型时出错: {str(e)}"
            logger.error(f"检查LightFM模型时出错: {str(e)}", exc_info=True)
        
        # 检查配置有效性
        try:
            config = recommendation_config.get_active_config(db)
            if config:
                # 验证权重和是否为1
                weight_sum = config.vector_weight + config.lightfm_weight
                if abs(weight_sum - 1.0) > 0.001:
                    health_status["configuration"]["status"] = "warning"
                    health_status["configuration"]["message"] = f"权重和({weight_sum})不为1，可能导致不正确的结果"
                else:
                    health_status["configuration"]["status"] = "healthy"
                    health_status["configuration"]["message"] = "推荐系统配置有效"
            else:
                health_status["configuration"]["status"] = "warning"
                health_status["configuration"]["message"] = "没有活跃的推荐配置，将使用默认值"
        except Exception as e:
            health_status["configuration"]["status"] = "error"
            health_status["configuration"]["message"] = f"检查配置时出错: {str(e)}"
            logger.error(f"检查推荐配置时出错: {str(e)}", exc_info=True)
        
        # 检查数据库中是否有足够的数据
        try:
            job_count = db.query(func.count(Job.id)).scalar()
            resume_count = db.query(func.count(Resume.id)).scalar()
            application_count = db.query(func.count(Application.id)).scalar()
            
            if job_count < 5 or resume_count < 5:
                health_status["database"]["status"] = "warning"
                health_status["database"]["message"] = f"数据量不足，当前有{job_count}个职位和{resume_count}个简历，协同过滤可能效果不佳"
            elif application_count < 10:
                health_status["database"]["status"] = "warning"
                health_status["database"]["message"] = f"申请记录不足({application_count}条)，协同过滤可能效果不佳"
            else:
                health_status["database"]["status"] = "healthy"
                health_status["database"]["message"] = f"数据充足: {job_count}个职位, {resume_count}个简历, {application_count}条申请记录"
        except Exception as e:
            health_status["database"]["status"] = "error"
            health_status["database"]["message"] = f"检查数据库时出错: {str(e)}"
            logger.error(f"检查数据库状态时出错: {str(e)}", exc_info=True)
        
        # 计算整体状态
        if any(component["status"] == "error" for component in health_status.values() if isinstance(component, dict)):
            health_status["overall_status"] = "error"
        elif any(component["status"] == "warning" for component in health_status.values() if isinstance(component, dict)):
            health_status["overall_status"] = "warning"
        else:
            health_status["overall_status"] = "healthy"
        
        # 返回结果
        return StandardResponse(
            success=True,
            message="推荐系统健康检查完成",
            data=health_status
        )
        
    except Exception as e:
        logger.error(f"执行推荐系统健康检查时出错: {str(e)}", exc_info=True)
        return StandardResponse(
            success=False,
            message=f"健康检查失败: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 