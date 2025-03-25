from fastapi import Request
import time
from typing import Dict, List, Optional, Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# 检查是否处于开发环境
DEV_MODE = os.environ.get("APP_ENV", "development") == "development" or settings.USE_SQLITE

# 根据环境选择适当的限速后端
if DEV_MODE:
    # 开发环境：使用内存后端
    from slowapi.errors import RateLimitExceeded
    
    # 创建基于内存的限速器
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200/minute"],
        storage_uri="memory://"
    )
    
    print("开发模式：使用内存速率限制后端")
else:
    # 生产环境：使用Redis后端
    try:
        # 创建基于Redis的限速器
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["200/minute"],
            storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        )
        print(f"生产模式：使用Redis速率限制后端 ({settings.REDIS_HOST}:{settings.REDIS_PORT})")
    except Exception as e:
        # 如果Redis连接失败，回退到内存存储
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["200/minute"],
            storage_uri="memory://"
        )
        print(f"警告：Redis连接失败，回退到内存速率限制后端: {str(e)}")

class RateLimiter:
    """简单的速率限制器实现"""
    
    def __init__(self):
        self.redis = None
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0
            )
            # 测试连接
            self.redis.ping()
        except Exception as e:
            print(f"Redis连接失败，使用内存缓存: {str(e)}")
            self.redis = None
            self.cache = {}
    
    def limit(self, rate_limit: str):
        """
        装饰器函数，用于限制API请求速率
        rate_limit: 格式为 "N/period" 其中N是数字，period是时间段（秒、分钟、小时）
        例如: "10/minute", "100/hour"
        """
        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                # 获取请求对象
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                if not request:
                    for key, value in kwargs.items():
                        if isinstance(value, Request):
                            request = value
                            break
                
                if not request:
                    # 如果找不到Request对象，无法执行速率限制
                    return await func(*args, **kwargs)
                
                # 解析速率限制
                limit_parts = rate_limit.split("/")
                if len(limit_parts) != 2:
                    return await func(*args, **kwargs)
                
                max_requests = int(limit_parts[0])
                period = self._get_period_seconds(limit_parts[1])
                
                # 获取唯一标识符（IP地址或认证用户）
                identifier = self._get_identifier(request)
                
                # 检查速率限制
                if not self._check_rate_limit(identifier, max_requests, period):
                    return Response(
                        content="Rate limit exceeded. Try again later.",
                        status_code=429
                    )
                
                return await func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def _get_period_seconds(self, period: str) -> int:
        """转换时间段为秒数"""
        if period == "second":
            return 1
        elif period == "minute":
            return 60
        elif period == "hour":
            return 3600
        elif period == "day":
            return 86400
        else:
            # 默认一分钟
            return 60
    
    def _get_identifier(self, request: Request) -> str:
        """获取请求的唯一标识符"""
        # 首选用户身份验证信息
        # 对于简化的示例，我们只使用IP地址
        client_host = request.client.host if request.client else "unknown"
        return f"{client_host}"
    
    def _check_rate_limit(self, identifier: str, max_requests: int, period: int) -> bool:
        """检查是否超过速率限制"""
        current_time = int(time.time())
        key = f"rate_limit:{identifier}:{period}"
        
        if self.redis:
            # 使用Redis实现
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(key, 0, current_time - period)
            pipe.zadd(key, {current_time: current_time})
            pipe.zcard(key)
            pipe.expire(key, period)
            results = pipe.execute()
            request_count = results[2]
        else:
            # 使用内存缓存实现
            if key not in self.cache:
                self.cache[key] = []
            
            # 移除过期的请求
            self.cache[key] = [t for t in self.cache[key] if t > current_time - period]
            
            # 添加当前请求
            self.cache[key].append(current_time)
            
            # 获取计数
            request_count = len(self.cache[key])
        
        # 检查是否超过限制
        return request_count <= max_requests


# 创建全局速率限制器实例
limiter = RateLimiter() 