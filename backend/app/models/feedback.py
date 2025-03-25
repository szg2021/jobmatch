from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base


class FeedbackType(str, enum.Enum):
    RELEVANT = "relevant"        # 相关
    NOT_RELEVANT = "not_relevant" # 不相关
    BOOKMARK = "bookmark"         # 收藏
    APPLIED = "applied"           # 已申请
    VIEWED = "viewed"             # 已查看
    SKIPPED = "skipped"           # 已跳过
    EXPLICIT = "explicit"         # 显式评分


class RecommendationFeedback(Base):
    """用户对推荐结果的反馈"""
    
    __tablename__ = "recommendation_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job.id"), nullable=True)
    resume_id = Column(Integer, ForeignKey("resume.id"), nullable=True)
    feedback_type = Column(String(50), nullable=False)
    rating = Column(Float, nullable=True)  # 1-5的评分，仅当feedback_type为EXPLICIT时使用
    comment = Column(Text, nullable=True)  # 用户评论
    algorithm = Column(String(50), nullable=True)  # 生成此推荐的算法
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="feedback")
    job = relationship("Job", back_populates="feedback")
    resume = relationship("Resume", back_populates="feedback")
    
    def __repr__(self):
        return f"<RecommendationFeedback(id={self.id}, user_id={self.user_id}, " \
               f"job_id={self.job_id}, resume_id={self.resume_id}, " \
               f"feedback_type={self.feedback_type})>"


class FeedbackMetrics(Base):
    """推荐系统表现指标"""
    
    __tablename__ = "feedback_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    algorithm = Column(String(50), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False, index=True)  # precision, recall, ndcg等
    value = Column(Float, nullable=False)
    config_id = Column(Integer, ForeignKey("recommendation_config.id"), nullable=True)
    details = Column(Text, nullable=True)  # 可以存储JSON格式的详细信息
    
    # 关系
    config = relationship("RecommendationConfig", back_populates="metrics")
    
    def __repr__(self):
        return f"<FeedbackMetrics(id={self.id}, date={self.date}, " \
               f"algorithm={self.algorithm}, metric_type={self.metric_type}, " \
               f"value={self.value})>" 