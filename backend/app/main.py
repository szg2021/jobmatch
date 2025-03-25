from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.api.api import api_router
from app.core.rate_limit import limiter
from app.core.logging import logger

# 获取应用日志记录器
app_logger = logging.getLogger("app.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI招聘推荐平台API",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 设置CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 速率限制异常处理
@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    app_logger.warning(f"请求频率限制触发: {request.client.host} - {request.url.path}")
    return JSONResponse(
        status_code=429,
        content={"detail": "请求频率过高，请稍后再试"}
    )

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    app_logger.error(f"全局异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "欢迎使用AI招聘推荐平台API"}


@app.on_event("startup")
async def startup_event():
    app_logger.info("应用启动")


@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("应用关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 