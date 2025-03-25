from fastapi import APIRouter

from app.api.endpoints import (
    login,
    users,
    resumes,
    jobs,
    admin,
    recommendations
)

api_router = APIRouter()

# 各模块路由
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"]) 