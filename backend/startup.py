import os
import logging
import subprocess
import sys
import asyncio
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("startup")

# 确保uploads目录存在
UPLOADS_DIR = Path("./uploads")
UPLOADS_DIR.mkdir(exist_ok=True)
logger.info(f"确保上传目录存在: {UPLOADS_DIR.absolute()}")

# 创建SQLite数据库
def init_sqlite_db():
    try:
        from sqlalchemy import create_engine
        from app.db.base import Base
        from app.core.config import settings

        # 如果使用SQLite作为开发数据库
        if settings.USE_SQLITE:
            logger.info(f"初始化SQLite数据库: {settings.SQLITE_DB}")
            
            # 获取SQLite数据库URI
            db_path = Path(f"./{settings.SQLITE_DB}")
            engine = create_engine(f"sqlite:///{settings.SQLITE_DB}")
            
            # 创建所有表
            Base.metadata.create_all(bind=engine)
            logger.info(f"SQLite数据库表创建成功: {db_path.absolute()}")
            
            return True
    except Exception as e:
        logger.error(f"初始化SQLite数据库时出错: {str(e)}")
        return False

# 检查环境变量
def check_environment():
    logger.info("检查环境变量...")
    env_file = Path("./.env")
    
    if not env_file.exists():
        logger.error("未找到.env文件，请确保配置文件存在")
        return False
    
    logger.info("环境变量检查通过")
    return True

# 初始化测试数据
async def init_test_data():
    try:
        logger.info("初始化测试数据...")
        
        # 导入数据初始化服务
        from sqlalchemy.orm import Session
        from app.db.session import SessionLocal
        from app.services.init_data import init_data
        
        # 创建数据库会话
        db = SessionLocal()
        try:
            # 调用初始化数据服务
            result = await init_data(db)
            if result:
                logger.info("测试数据初始化完成")
            else:
                logger.warning("测试数据初始化过程中出现问题")
            
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"初始化测试数据时出错: {str(e)}")
        return False

# 启动应用程序
def start_application():
    try:
        logger.info("正在启动应用...")
        # 在Windows中使用shell=True参数执行命令
        # 这样在Windows环境下可以更好地支持命令执行
        cmd = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        subprocess.run(cmd, shell=True)
        return True
    except Exception as e:
        logger.error(f"启动应用时出错: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("======== 开始启动AI招聘推荐平台后端 ========")
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 初始化数据库
    if not init_sqlite_db():
        sys.exit(1)
    
    # 初始化测试数据
    asyncio.run(init_test_data())
    
    # 启动应用
    start_application() 