from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import logging

from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.crud.crud_recommendation_config import recommendation_config
from app.schemas.recommendation_config import (
    RecommendationConfig,
    RecommendationConfigCreate,
    RecommendationConfigUpdate,
    RecommendationConfigList
)
from app.services.lightfm_recommendation_service import prepare_and_train_lightfm

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[RecommendationConfigList])
def get_configs(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """获取所有推荐配置列表"""
    configs = db.query(recommendation_config.model).offset(skip).limit(limit).all()
    return configs


@router.get("/active", response_model=RecommendationConfig)
def get_active_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
) -> Any:
    """获取当前活跃配置"""
    config = recommendation_config.get_active_config(db)
    if not config:
        # 如果没有活跃配置，尝试创建默认配置
        config = recommendation_config.create_default_config(db)
        if not config:
            raise HTTPException(status_code=404, detail="无活跃配置")
    return config


@router.post("/", response_model=RecommendationConfig)
def create_config(
    *,
    db: Session = Depends(get_db),
    config_in: RecommendationConfigCreate,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """创建新的推荐配置"""
    # 验证权重和为1
    if abs(config_in.vector_weight + config_in.lightfm_weight - 1.0) > 0.001:
        raise HTTPException(
            status_code=400,
            detail="向量搜索权重和LightFM权重之和必须等于1"
        )
    
    # 如果设置为活跃，则需要禁用其他配置
    if config_in.is_active:
        db.query(recommendation_config.model).update({"is_active": False})
    
    config = recommendation_config.create(db, obj_in=config_in)
    return config


@router.get("/{config_id}", response_model=RecommendationConfig)
def get_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """获取特定ID的配置"""
    config = recommendation_config.get(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"配置ID {config_id} 不存在")
    return config


@router.put("/{config_id}", response_model=RecommendationConfig)
def update_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    config_in: RecommendationConfigUpdate,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """更新特定ID的配置"""
    config = recommendation_config.get(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"配置ID {config_id} 不存在")
    
    # 验证权重和为1
    if (
        config_in.vector_weight is not None and
        config_in.lightfm_weight is not None and
        abs(config_in.vector_weight + config_in.lightfm_weight - 1.0) > 0.001
    ):
        raise HTTPException(
            status_code=400,
            detail="向量搜索权重和LightFM权重之和必须等于1"
        )
    
    # 如果设置为活跃，则需要禁用其他配置
    if config_in.is_active:
        db.query(recommendation_config.model).filter(recommendation_config.model.id != config_id).update({"is_active": False})
    
    config = recommendation_config.update(db, db_obj=config, obj_in=config_in)
    return config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """删除特定ID的配置"""
    config = recommendation_config.get(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"配置ID {config_id} 不存在")
    
    # 不允许删除活跃配置
    if config.is_active:
        raise HTTPException(status_code=400, detail="不能删除当前活跃的配置")
    
    recommendation_config.remove(db, id=config_id)
    return None


@router.post("/{config_id}/activate", response_model=RecommendationConfig)
def activate_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """激活指定ID的配置（同时禁用其他配置）"""
    # 首先检查配置是否存在
    config = recommendation_config.get(db, id=config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    try:
        config = recommendation_config.set_active_config(db, id=config_id)
        if not config:
            raise HTTPException(status_code=500, detail="激活配置失败")
        return config
    except Exception as e:
        # 捕获可能的数据库错误
        logger.error(f"激活配置时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"激活配置失败: {str(e)}")


# 训练状态变量
training_in_progress = False


@router.post("/training/trigger", status_code=202)
async def trigger_model_training(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
) -> Any:
    """手动触发模型训练"""
    global training_in_progress
    
    if training_in_progress:
        return {"message": "训练任务已在进行中，无法启动新任务"}
    
    try:
        # 标记训练开始
        training_in_progress = True
        
        # 获取活跃配置
        config = recommendation_config.get_active_config(db)
        if not config:
            config = recommendation_config.create_default_config(db)
            if not config:
                raise HTTPException(status_code=500, detail="无法获取或创建配置")
        
        # 启动训练任务
        async def train_task():
            global training_in_progress
            try:
                config_dict = recommendation_config.get_config_for_training(db)
                success = await prepare_and_train_lightfm(db, config_dict)
                
                if success:
                    # 更新最后训练时间
                    from datetime import datetime
                    config.last_trained = datetime.now()
                    db.add(config)
                    db.commit()
                    logger.info("模型训练成功完成")
                else:
                    logger.error("模型训练失败")
            except Exception as e:
                logger.error(f"训练过程中出错: {str(e)}")
            finally:
                training_in_progress = False
        
        # 在后台运行训练任务
        background_tasks.add_task(train_task)
        
        return {"message": "训练任务已成功启动，您可以通过状态API查看进度"}
    except Exception as e:
        # 重置训练状态
        training_in_progress = False
        logger.error(f"触发训练失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"触发训练失败: {str(e)}")


@router.get("/training/status")
def get_training_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
) -> Any:
    """获取训练状态"""
    global training_in_progress
    
    # 获取活跃配置以获取上次训练时间
    config = recommendation_config.get_active_config(db)
    last_trained = config.last_trained if config else None
    
    return {
        "in_progress": training_in_progress,
        "last_trained": last_trained
    } 