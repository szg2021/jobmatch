from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RecommendationConfigBase(BaseModel):
    """基础推荐系统配置模式"""
    learning_rate: float = Field(default=0.05, ge=0.001, le=1.0, description="学习率 (0.001-1.0)")
    loss_function: str = Field(default="warp", description="损失函数 (warp/bpr/logistic)")
    embedding_dim: int = Field(default=64, ge=16, le=256, description="嵌入维度 (16-256)")
    user_alpha: float = Field(default=1e-6, ge=0, le=1.0, description="用户正则化参数 (0-1.0)")
    item_alpha: float = Field(default=1e-6, ge=0, le=1.0, description="物品正则化参数 (0-1.0)")
    epochs: int = Field(default=30, ge=5, le=100, description="训练轮数 (5-100)")
    num_threads: int = Field(default=4, ge=1, le=16, description="训练线程数 (1-16)")
    vector_weight: float = Field(default=0.6, ge=0.0, le=1.0, description="向量搜索权重 (0.0-1.0)")
    lightfm_weight: float = Field(default=0.4, ge=0.0, le=1.0, description="LightFM推荐权重 (0.0-1.0)")
    training_schedule: str = Field(default="0 2 * * *", description="定时训练计划 (Cron表达式)")
    train_on_startup: bool = Field(default=True, description="应用启动时是否训练")
    max_recommendations: int = Field(default=10, ge=1, le=50, description="最大推荐数量 (1-50)")
    active: bool = Field(default=True, description="是否启用此配置")
    

class RecommendationConfigCreate(RecommendationConfigBase):
    """创建推荐系统配置的输入模式"""
    pass


class RecommendationConfigUpdate(BaseModel):
    """更新推荐系统配置的输入模式"""
    learning_rate: Optional[float] = Field(default=None, ge=0.001, le=1.0, description="学习率 (0.001-1.0)")
    loss_function: Optional[str] = Field(default=None, description="损失函数 (warp/bpr/logistic)")
    embedding_dim: Optional[int] = Field(default=None, ge=16, le=256, description="嵌入维度 (16-256)")
    user_alpha: Optional[float] = Field(default=None, ge=0, le=1.0, description="用户正则化参数 (0-1.0)")
    item_alpha: Optional[float] = Field(default=None, ge=0, le=1.0, description="物品正则化参数 (0-1.0)")
    epochs: Optional[int] = Field(default=None, ge=5, le=100, description="训练轮数 (5-100)")
    num_threads: Optional[int] = Field(default=None, ge=1, le=16, description="训练线程数 (1-16)")
    vector_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="向量搜索权重 (0.0-1.0)")
    lightfm_weight: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="LightFM推荐权重 (0.0-1.0)")
    training_schedule: Optional[str] = Field(default=None, description="定时训练计划 (Cron表达式)")
    train_on_startup: Optional[bool] = Field(default=None, description="应用启动时是否训练")
    max_recommendations: Optional[int] = Field(default=None, ge=1, le=50, description="最大推荐数量 (1-50)")
    active: Optional[bool] = Field(default=None, description="是否启用此配置")


class RecommendationConfigInDBBase(RecommendationConfigBase):
    """数据库中存储的配置响应基础模式"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RecommendationConfig(RecommendationConfigInDBBase):
    """完整的推荐系统配置响应模式"""
    pass


class RecommendationConfigList(BaseModel):
    """配置列表响应模式"""
    items: list[RecommendationConfig]
    total: int 