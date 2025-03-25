import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 日志配置
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIR = Path("logs")

# 确保日志目录存在
LOG_DIR.mkdir(exist_ok=True)

# 创建日志文件名，包含日期
log_filename = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

# 配置根日志记录器
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)

# 创建应用日志记录器
logger = logging.getLogger("app")

# 捕获未处理的异常
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # 正常退出，不记录堆栈跟踪
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.error("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))

# 设置未捕获异常处理器
sys.excepthook = handle_exception 