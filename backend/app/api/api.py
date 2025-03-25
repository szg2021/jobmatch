from fastapi import APIRouter

from app.api.endpoints import auth, users, resumes, jobs, recommendations, admin

api_router = APIRouter()

# 各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["简历"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["岗位"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["推荐"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理"]) 