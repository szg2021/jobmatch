from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.user_service import check_if_admin

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_admin)
) -> Any:
    """
    获取系统统计信息（仅管理员）
    """
    user_count = db.query(User).count()
    company_count = db.query(User).filter(User.role == "company").count()
    jobseeker_count = db.query(User).filter(User.role == "jobseeker").count()
    
    # 这里可以添加更多统计信息，如简历数量、职位数量等
    # 后续可以根据需要扩展
    
    return {
        "user_count": user_count,
        "company_count": company_count,
        "jobseeker_count": jobseeker_count,
    }


@router.get("/settings", response_model=Dict[str, Any])
async def get_system_settings(
    current_user: User = Depends(check_if_admin)
) -> Any:
    """
    获取系统设置（仅管理员）
    """
    # 示例设置，实际中可能从数据库或配置文件中读取
    return {
        "ai_models": {
            "embedding_model": "text-embedding-ada-002",
            "llm_model": "gpt-3.5-turbo",
        },
        "matching_settings": {
            "min_similarity_score": 0.6,
            "max_recommendations": 10,
        },
        "system_settings": {
            "allow_registration": True,
            "maintenance_mode": False,
        }
    }


@router.put("/settings", response_model=Dict[str, Any])
async def update_system_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(check_if_admin)
) -> Any:
    """
    更新系统设置（仅管理员）
    """
    # 在实际应用中，这里会将设置保存到数据库或配置文件
    # 这里简单返回接收到的设置
    return settings 