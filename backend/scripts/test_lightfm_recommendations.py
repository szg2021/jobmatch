#!/usr/bin/env python
"""
测试LightFM推荐系统的功能

此脚本测试LightFM推荐系统的准备、训练和推荐功能。
LightFM推荐系统测试脚本
测试方法: python -m scripts.test_lightfm_recommendations
"""
import sys
import os
import asyncio
import logging
from sqlalchemy import func

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.document import Resume, Job
from app.services.lightfm_recommendation_service import (
    lightfm_recommender,
    prepare_and_train_lightfm,
    get_lightfm_job_recommendations,
    get_lightfm_resume_recommendations
)

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("test_lightfm")

async def test_lightfm_recommendations():
    """测试LightFM推荐功能"""
    logger.info("开始测试LightFM推荐系统...")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 准备数据并训练模型
        success = await prepare_and_train_lightfm(db)
        if not success:
            logger.error("LightFM模型训练失败")
            return
        
        # 获取一个随机简历来测试
        resume = db.query(Resume).order_by(func.random()).first()
        if not resume:
            logger.error("数据库中没有简历数据")
            return
        
        # 获取一个随机岗位来测试
        job = db.query(Job).filter(Job.is_active == True).order_by(func.random()).first()
        if not job:
            logger.error("数据库中没有活跃的岗位数据")
            return
        
        # 测试为简历推荐岗位
        logger.info(f"测试为简历ID: {resume.id} 推荐岗位")
        job_recommendations = await get_lightfm_job_recommendations(db, resume.id, limit=5)
        
        if job_recommendations:
            logger.info(f"为简历 {resume.id} 推荐了 {len(job_recommendations)} 个岗位")
            for i, rec in enumerate(job_recommendations, 1):
                job_id = rec.get("job_id")
                score = rec.get("score")
                job_obj = db.query(Job).filter(Job.id == job_id).first()
                job_title = job_obj.title if job_obj else "未知"
                logger.info(f"  {i}. 岗位ID: {job_id}, 标题: {job_title}, 分数: {score:.4f}")
        else:
            logger.warning(f"简历 {resume.id} 没有收到岗位推荐")
        
        # 测试为岗位推荐简历
        logger.info(f"测试为岗位ID: {job.id} 推荐简历")
        resume_recommendations = await get_lightfm_resume_recommendations(db, job.id, limit=5)
        
        if resume_recommendations:
            logger.info(f"为岗位 {job.id} 推荐了 {len(resume_recommendations)} 份简历")
            for i, rec in enumerate(resume_recommendations, 1):
                resume_id = rec.get("resume_id")
                score = rec.get("score")
                resume_obj = db.query(Resume).filter(Resume.id == resume_id).first()
                resume_title = resume_obj.title if resume_obj else "未知"
                logger.info(f"  {i}. 简历ID: {resume_id}, 标题: {resume_title}, 分数: {score:.4f}")
        else:
            logger.warning(f"岗位 {job.id} 没有收到简历推荐")
        
        logger.info("LightFM推荐系统测试完成")
    except Exception as e:
        logger.exception(f"测试过程中发生错误: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_lightfm_recommendations()) 