#!/usr/bin/env python
import asyncio
import logging
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.services.vector_search_service import vector_search_service
from app.services.recommendation_service import (
    get_recommended_jobs,
    get_recommended_resumes,
    initialize_vector_search
)
from app.core.tasks import initialize_search_services
from app.models.job import Job
from app.models.resume import Resume

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_recommendation_flow")

async def test_recommendation_flow():
    """测试推荐系统完整流程"""
    logger.info("=== 开始测试推荐系统流程 ===")
    db = None
    
    try:
        # 1. 获取数据库会话
        logger.info("建立数据库连接...")
        db = SessionLocal()
        
        # 2. 初始化向量搜索服务
        logger.info("初始化向量搜索服务...")
        initialized = await initialize_search_services(db)
        if not initialized:
            logger.error("向量搜索服务初始化失败")
            return False
        
        logger.info("向量搜索服务初始化成功")
        
        # 3. 获取一个测试简历和职位
        logger.info("获取测试数据...")
        resume = db.query(Resume).first()
        job = db.query(Job).first()
        
        if not resume:
            logger.error("数据库中没有简历数据，无法进行测试")
            return False
            
        if not job:
            logger.error("数据库中没有职位数据，无法进行测试")
            return False
            
        logger.info(f"获取到测试简历 ID: {resume.id}, 标题: {resume.title}")
        logger.info(f"获取到测试职位 ID: {job.id}, 标题: {job.title}")
        
        # 4. 测试获取职位推荐
        logger.info("测试获取职位推荐...")
        job_recommendations = await get_recommended_jobs(db, resume.id, limit=5, include_details=True)
        
        if not job_recommendations:
            logger.warning(f"未找到简历 {resume.id} 的职位推荐")
        else:
            logger.info(f"成功获取 {len(job_recommendations)} 个职位推荐:")
            for i, rec in enumerate(job_recommendations[:3], 1):
                logger.info(f"  {i}. {rec['title']} - 匹配度: {rec['match_score']:.2f} - 算法: {rec['algorithms']}")
        
        # 5. 测试获取简历推荐
        logger.info("测试获取简历推荐...")
        resume_recommendations = await get_recommended_resumes(db, job.id, limit=5, include_details=True)
        
        if not resume_recommendations:
            logger.warning(f"未找到职位 {job.id} 的简历推荐")
        else:
            logger.info(f"成功获取 {len(resume_recommendations)} 个简历推荐:")
            for i, rec in enumerate(resume_recommendations[:3], 1):
                logger.info(f"  {i}. {rec['title']} - 匹配度: {rec['match_score']:.2f} - 算法: {rec['algorithms']}")
        
        # 6. 测试向量搜索服务的直接方法
        logger.info("测试向量搜索服务直接方法...")
        job_vector_recommendations = await vector_search_service.get_vector_job_recommendations(db, resume.id, limit=5)
        
        if not job_vector_recommendations:
            logger.warning(f"向量搜索未找到简历 {resume.id} 的职位推荐")
        else:
            logger.info(f"向量搜索成功获取 {len(job_vector_recommendations)} 个职位推荐")
        
        # 测试成功
        logger.info("=== 推荐系统流程测试完成 ===")
        return True
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}", exc_info=True)
        return False
    finally:
        if db:
            db.close()

async def main():
    """主函数"""
    success = await test_recommendation_flow()
    if not success:
        logger.error("推荐系统流程测试失败")
        sys.exit(1)
    else:
        logger.info("推荐系统流程测试成功")

if __name__ == "__main__":
    asyncio.run(main()) 