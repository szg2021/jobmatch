import logging
import threading
from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Any

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.rate_limit import limiter
from app.core.tasks import start_background_tasks
from app.db.session import SessionLocal

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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

# 注册API路由
app.include_router(
    api_router,
    prefix=settings.API_V1_STR
)

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行的操作
    """
    logger.info("=== 应用启动 ===")
    
    # 启动后台任务（包括初始化向量搜索和训练LightFM模型）
    logger.info("启动后台任务...")
    background_thread = threading.Thread(target=start_background_tasks)
    background_thread.daemon = True
    background_thread.start()
    logger.info("后台任务线程已启动")

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时执行的操作
    """
    logger.info("=== 应用关闭 ===")

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    """
    logger.error(f"未捕获的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "服务器内部错误，请稍后再试"}
    )

# 健康检查端点
@app.get("/health")
async def health_check():
    """
    健康检查API
    """
    return {"status": "ok", "service": settings.PROJECT_NAME}

# 状态检查端点，包括搜索服务状态
@app.get("/status")
async def status_check():
    """
    服务状态检查API，包括推荐系统各组件状态
    """
    from app.core.tasks import vector_search_initialized, last_trained_time, training_in_progress
    
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "recommendation_system": {
            "vector_search_initialized": vector_search_initialized,
            "last_model_training": last_trained_time.isoformat() if last_trained_time else None,
            "training_in_progress": training_in_progress
        }
    }

# 数据库会话依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "欢迎使用求职推荐系统API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 