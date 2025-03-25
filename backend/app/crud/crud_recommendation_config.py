from typing import Dict, List, Any, Optional, Union
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.recommendation_config import RecommendationConfig
from app.schemas.recommendation_config import RecommendationConfigCreate, RecommendationConfigUpdate

import logging

logger = logging.getLogger(__name__)

class CRUDRecommendationConfig(CRUDBase[RecommendationConfig, RecommendationConfigCreate, RecommendationConfigUpdate]):
    """推荐系统配置的CRUD操作"""
    
    def get_active_config(self, db: Session) -> Optional[RecommendationConfig]:
        """获取当前激活状态的配置"""
        return db.query(self.model).filter(self.model.is_active == True).first()
    
    def set_active_config(self, db: Session, id: int) -> Optional[RecommendationConfig]:
        """设置指定ID的配置为激活状态，同时禁用其他配置"""
        try:
            # 先禁用所有配置
            db.query(self.model).update({RecommendationConfig.is_active: False})
            
            # 然后激活指定ID的配置
            config = db.query(self.model).filter(self.model.id == id).first()
            if config:
                config.is_active = True
                db.commit()
                db.refresh(config)
                logger.info(f"已激活配置ID {id}")
                return config
            else:
                logger.warning(f"未找到配置ID {id}")
                return None
        except Exception as e:
            db.rollback()
            logger.error(f"激活配置时出错: {str(e)}")
            return None
    
    def create_default_config(self, db: Session) -> Optional[RecommendationConfig]:
        """如果不存在配置，创建默认配置；否则返回活跃配置"""
        config_count = db.query(self.model).count()
        if config_count == 0:
            default_config = RecommendationConfigCreate(
                name="默认配置",
                description="系统默认配置",
                learning_rate=0.05,
                loss_function="warp",
                embedding_dim=64,
                user_alpha=1e-6,
                item_alpha=1e-6,
                epochs=30,
                num_threads=4,
                train_schedule="0 2 * * *",  # 每天凌晨2点
                train_on_startup=True,
                vector_weight=0.6,
                lightfm_weight=0.4,
                max_recommendations=10,
                is_active=True
            )
            logger.info("创建默认推荐配置")
            return self.create(db=db, obj_in=default_config)
        else:
            # 返回现有的活跃配置
            config = self.get_active_config(db)
            if not config:
                # 如果没有活跃配置，激活第一个
                first_config = db.query(self.model).first()
                return self.set_active_config(db, first_config.id)
            return config
    
    def get_config_for_training(self, db: Session) -> Dict[str, Any]:
        """获取用于训练的配置参数"""
        config = self.get_active_config(db)
        if not config:
            config = self.create_default_config(db)
            # 如果仍然为空，使用硬编码默认值
            if not config:
                logger.warning("无法获取或创建配置，使用默认值")
                return {
                    "learning_rate": 0.05,
                    "loss_function": "warp",
                    "embedding_dim": 64,
                    "user_alpha": 1e-6,
                    "item_alpha": 1e-6,
                    "epochs": 30,
                    "num_threads": 4,
                    "vector_weight": 0.6,
                    "lightfm_weight": 0.4,
                    "max_recommendations": 10
                }
        
        # 返回训练所需的参数
        return {
            "learning_rate": float(config.learning_rate),
            "loss_function": config.loss_function,
            "embedding_dim": int(config.embedding_dim),
            "user_alpha": float(config.user_alpha),
            "item_alpha": float(config.item_alpha),
            "epochs": int(config.epochs),
            "num_threads": int(config.num_threads),
            "vector_weight": float(config.vector_weight),
            "lightfm_weight": float(config.lightfm_weight),
            "max_recommendations": int(config.max_recommendations)
        }


# 创建单例实例
recommendation_config = CRUDRecommendationConfig(RecommendationConfig) 