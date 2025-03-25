from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func

from app.db.base_class import Base


class RecommendationConfig(Base):
    """
    LightFM推荐系统配置模型
    存储推荐系统的各种参数设置
    """
    __tablename__ = "recommendation_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # LightFM模型参数
    learning_rate = Column(Float, default=0.05, comment="学习率")
    loss_function = Column(String(50), default="warp", comment="损失函数(warp/bpr/logistic)")
    embedding_dim = Column(Integer, default=64, comment="嵌入维度")
    user_alpha = Column(Float, default=1e-6, comment="用户正则化参数")
    item_alpha = Column(Float, default=1e-6, comment="物品正则化参数")
    epochs = Column(Integer, default=30, comment="训练轮数")
    num_threads = Column(Integer, default=4, comment="训练线程数")
    
    # 推荐混合权重
    vector_weight = Column(Float, default=0.6, comment="向量搜索权重")
    lightfm_weight = Column(Float, default=0.4, comment="LightFM推荐权重")
    
    # 训练设置
    train_schedule = Column(String(50), default="0 2 * * *", comment="定时训练Cron表达式")
    train_on_startup = Column(Boolean, default=True, comment="应用启动时是否训练")
    last_trained = Column(DateTime, nullable=True, comment="最后一次训练时间")
    
    # 其他设置
    max_recommendations = Column(Integer, default=10, comment="最大推荐数量")
    is_active = Column(Boolean, default=False, comment="是否启用此配置")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<RecommendationConfig(id={self.id}, loss_function={self.loss_function}, embedding_dim={self.embedding_dim})>" 