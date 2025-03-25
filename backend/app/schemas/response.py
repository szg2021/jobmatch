from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field
from fastapi import status

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    """标准API响应模型"""
    
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    status_code: int = Field(status.HTTP_200_OK, description="HTTP状态码")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "操作成功",
                "data": None,
                "status_code": 200
            }
        } 