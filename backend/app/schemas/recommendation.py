from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.schemas.job import Job
from app.schemas.resume import Resume
from app.schemas.user import User


class MatchDetail(BaseModel):
    """匹配详情模型"""
    similarity_score: float = Field(..., description="相似度分数")
    matched_skills: List[str] = Field(default=[], description="匹配的技能列表")
    experience_match: Optional[float] = Field(default=None, description="经验匹配程度")
    education_match: Optional[float] = Field(default=None, description="教育背景匹配程度")
    location_match: Optional[bool] = Field(default=None, description="位置是否匹配")


class JobRecommendationResponse(BaseModel):
    """职位推荐响应模型"""
    id: int = Field(..., description="职位ID")
    title: str = Field(..., description="职位标题")
    company: str = Field(..., description="公司名称")
    match_score: float = Field(..., description="匹配分数")
    algorithms: List[str] = Field(..., description="推荐算法类型列表，如 ['lightfm', 'vector']")
    match_details: Optional[MatchDetail] = Field(default=None, description="匹配详情")
    description: Optional[str] = Field(default=None, description="职位描述")
    requirements: Optional[str] = Field(default=None, description="职位要求")
    location: Optional[str] = Field(default=None, description="工作地点")
    salary_min: Optional[int] = Field(default=None, description="最低薪资")
    salary_max: Optional[int] = Field(default=None, description="最高薪资")
    job_type: Optional[str] = Field(default=None, description="工作类型")
    experience_required: Optional[int] = Field(default=None, description="要求经验年限")
    
    class Config:
        orm_mode = True


class ResumeRecommendationResponse(BaseModel):
    """简历推荐响应模型"""
    id: int = Field(..., description="简历ID")
    title: str = Field(..., description="简历标题")
    user: Optional[User] = Field(default=None, description="用户信息")
    match_score: float = Field(..., description="匹配分数")
    algorithms: List[str] = Field(..., description="推荐算法类型列表，如 ['lightfm', 'vector']")
    match_details: Optional[MatchDetail] = Field(default=None, description="匹配详情")
    summary: Optional[str] = Field(default=None, description="个人简介")
    skills: Optional[List[str]] = Field(default=None, description="技能列表")
    experience: Optional[int] = Field(default=None, description="工作经验年限")
    education_level: Optional[str] = Field(default=None, description="教育程度")
    
    class Config:
        orm_mode = True


class RecommendationMetrics(BaseModel):
    """推荐系统评估指标"""
    precision: float = Field(..., description="准确率")
    recall: float = Field(..., description="召回率")
    f1_score: float = Field(..., description="F1分数")
    mean_average_precision: float = Field(..., description="平均准确率均值")
    coverage: float = Field(..., description="覆盖率")
    diversity: float = Field(..., description="多样性")


class RecommendationConfig(BaseModel):
    """推荐系统配置参数基础模型"""
    id: Optional[int] = Field(None, description="配置ID")
    name: str = Field(..., description="配置名称")
    description: Optional[str] = Field(None, description="配置描述")
    is_active: bool = Field(False, description="是否激活")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    
    # LightFM模型参数
    no_components: int = Field(30, description="隐因子数量")
    learning_rate: float = Field(0.05, description="学习率")
    loss: str = Field("warp", description="损失函数")
    max_sampled: int = Field(10, description="负采样数量")
    
    # 向量搜索参数
    vector_search_weight: float = Field(0.5, description="向量搜索权重")
    lightfm_weight: float = Field(0.5, description="协同过滤权重")
    skill_match_weight: float = Field(0.3, description="技能匹配权重")
    
    class Config:
        orm_mode = True


class RecommendationConfigCreate(BaseModel):
    """推荐系统配置创建模型"""
    name: str = Field(..., description="配置名称")
    description: Optional[str] = Field(None, description="配置描述")
    is_active: bool = Field(False, description="是否激活")
    
    # LightFM模型参数
    no_components: Optional[int] = Field(30, description="隐因子数量")
    learning_rate: Optional[float] = Field(0.05, description="学习率")
    loss: Optional[str] = Field("warp", description="损失函数")
    max_sampled: Optional[int] = Field(10, description="负采样数量")
    
    # 向量搜索参数
    vector_search_weight: Optional[float] = Field(0.5, description="向量搜索权重")
    lightfm_weight: Optional[float] = Field(0.5, description="协同过滤权重")
    skill_match_weight: Optional[float] = Field(0.3, description="技能匹配权重")


class RecommendationConfigUpdate(BaseModel):
    """推荐系统配置更新模型"""
    name: Optional[str] = Field(None, description="配置名称")
    description: Optional[str] = Field(None, description="配置描述")
    is_active: Optional[bool] = Field(None, description="是否激活")
    
    # LightFM模型参数
    no_components: Optional[int] = Field(None, description="隐因子数量")
    learning_rate: Optional[float] = Field(None, description="学习率")
    loss: Optional[str] = Field(None, description="损失函数")
    max_sampled: Optional[int] = Field(None, description="负采样数量")
    
    # 向量搜索参数
    vector_search_weight: Optional[float] = Field(None, description="向量搜索权重")
    lightfm_weight: Optional[float] = Field(None, description="协同过滤权重")
    skill_match_weight: Optional[float] = Field(None, description="技能匹配权重") 