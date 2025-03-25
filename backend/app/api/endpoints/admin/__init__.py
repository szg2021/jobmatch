from fastapi import APIRouter

from app.api.endpoints.admin import (
    users,
    dashboard,
    jobs,
    recommendation_config,
    recommendation_management
)

router = APIRouter()

# 管理员路由
router.include_router(users.router, prefix="/users", tags=["管理员-用户"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["管理员-仪表盘"])
router.include_router(jobs.router, prefix="/jobs", tags=["管理员-岗位"])
router.include_router(recommendation_config.router, prefix="/recommendation-config", tags=["管理员-推荐配置"])
router.include_router(recommendation_management.router, prefix="/recommendation", tags=["管理员-推荐管理"]) 