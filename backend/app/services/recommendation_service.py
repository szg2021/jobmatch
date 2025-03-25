from typing import List, Dict, Any, Optional
import os
import logging
import time
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.document import Resume, Job
from app.models.user import User
from app.services.lightfm_recommendation_service import (
    get_lightfm_job_recommendations,
    get_lightfm_resume_recommendations,
    is_lightfm_ready
)
from app.services.vector_search_service import (
    vector_search_service,
    get_vector_job_recommendations,
    get_vector_resume_recommendations
)
from app.crud.crud_recommendation_config import recommendation_config

# 获取日志记录器
logger = logging.getLogger("app.services.recommendation")

# 检查是否处于开发环境
DEV_MODE = os.environ.get("APP_ENV", "development") == "development" or settings.USE_SQLITE

# 推荐结果缓存
recommendation_cache = {
    "jobs": {},     # 职位推荐缓存: {resume_id: {"results": [...], "timestamp": datetime, "config_id": id}}
    "resumes": {}   # 简历推荐缓存: {job_id: {"results": [...], "timestamp": datetime, "config_id": id}}
}

# 缓存配置
CACHE_TTL = 3600  # 缓存有效期(秒)
DEFAULT_CACHE_ENABLED = True  # 默认是否启用缓存

# 清理过期缓存
def clean_expired_cache():
    """清理过期的缓存项"""
    now = datetime.now()
    expired_count = 0
    
    # 清理职位推荐缓存
    expired_resume_ids = []
    for resume_id, cache_item in recommendation_cache["jobs"].items():
        if (now - cache_item["timestamp"]).total_seconds() > CACHE_TTL:
            expired_resume_ids.append(resume_id)
            expired_count += 1
    
    for resume_id in expired_resume_ids:
        del recommendation_cache["jobs"][resume_id]
    
    # 清理简历推荐缓存
    expired_job_ids = []
    for job_id, cache_item in recommendation_cache["resumes"].items():
        if (now - cache_item["timestamp"]).total_seconds() > CACHE_TTL:
            expired_job_ids.append(job_id)
            expired_count += 1
    
    for job_id in expired_job_ids:
        del recommendation_cache["resumes"][job_id]
    
    if expired_count > 0:
        logger.info(f"已清理 {expired_count} 条过期缓存")

# 定期清理缓存的函数，可以由任务调度器调用
async def schedule_cache_cleanup():
    """定期清理缓存的任务"""
    clean_expired_cache()

# 缓存职位推荐结果
def cache_job_recommendations(resume_id: int, results: List[Dict[str, Any]], config_id: int):
    """缓存职位推荐结果"""
    recommendation_cache["jobs"][resume_id] = {
        "results": results,
        "timestamp": datetime.now(),
        "config_id": config_id
    }
    logger.debug(f"已缓存简历 {resume_id} 的职位推荐结果")

# 缓存简历推荐结果
def cache_resume_recommendations(job_id: int, results: List[Dict[str, Any]], config_id: int):
    """缓存简历推荐结果"""
    recommendation_cache["resumes"][job_id] = {
        "results": results,
        "timestamp": datetime.now(),
        "config_id": config_id
    }
    logger.debug(f"已缓存职位 {job_id} 的简历推荐结果")

# 获取职位推荐缓存
def get_cached_job_recommendations(resume_id: int, config_id: int) -> Optional[List[Dict[str, Any]]]:
    """获取缓存的职位推荐结果"""
    if resume_id in recommendation_cache["jobs"]:
        cache_item = recommendation_cache["jobs"][resume_id]
        
        # 检查是否过期
        if (datetime.now() - cache_item["timestamp"]).total_seconds() <= CACHE_TTL:
            # 检查配置是否变更
            if cache_item["config_id"] == config_id:
                logger.debug(f"使用缓存的简历 {resume_id} 职位推荐结果")
                return cache_item["results"]
    
    return None

# 获取简历推荐缓存
def get_cached_resume_recommendations(job_id: int, config_id: int) -> Optional[List[Dict[str, Any]]]:
    """获取缓存的简历推荐结果"""
    if job_id in recommendation_cache["resumes"]:
        cache_item = recommendation_cache["resumes"][job_id]
        
        # 检查是否过期
        if (datetime.now() - cache_item["timestamp"]).total_seconds() <= CACHE_TTL:
            # 检查配置是否变更
            if cache_item["config_id"] == config_id:
                logger.debug(f"使用缓存的职位 {job_id} 简历推荐结果")
                return cache_item["results"]
    
    return None

# 使用缓存修改推荐函数
async def get_recommended_jobs(
    db: Session,
    resume_id: int,
    limit: int = None,
    include_details: bool = True,
    use_cache: bool = DEFAULT_CACHE_ENABLED
) -> List[Dict[str, Any]]:
    """
    获取推荐职位列表
    
    Args:
        db: 数据库会话
        resume_id: 简历ID
        limit: 返回结果数量限制
        include_details: 是否包含详细信息
        use_cache: 是否使用缓存
        
    Returns:
        推荐职位列表
    """
    try:
        start_time = time.time()
        
        # 获取当前配置或使用默认值
        config = recommendation_config.get_active_config(db)
        if not config:
            logger.warning("找不到活跃的推荐配置，将创建默认配置")
            config = recommendation_config.create_default_config(db)
        
        # 如果仍没有配置，使用默认值
        if not config:
            logger.warning("无法创建默认配置，使用硬编码的默认值")
            max_recommendations = 10
            vector_weight = 0.6
            lightfm_weight = 0.4
            config_id = 0
        else:
            max_recommendations = config.max_recommendations
            vector_weight = config.vector_weight
            lightfm_weight = config.lightfm_weight
            config_id = config.id
            
            # 确保权重总和为1
            if abs(vector_weight + lightfm_weight - 1.0) > 0.001:
                logger.warning(f"向量权重({vector_weight})和LightFM权重({lightfm_weight})之和不为1，将进行归一化")
                total = vector_weight + lightfm_weight
                if total > 0:
                    vector_weight = vector_weight / total
                    lightfm_weight = lightfm_weight / total
                else:
                    # 如果总和为0或负数，设置默认值
                    vector_weight = 0.6
                    lightfm_weight = 0.4
                    logger.warning(f"权重总和异常，已重置为默认值：向量权重={vector_weight}，LightFM权重={lightfm_weight}")
        
        # 应用结果数量限制
        if limit is None:
            limit = max_recommendations
        elif limit <= 0:
            logger.warning(f"无效的结果数量限制: {limit}，将使用默认值: {max_recommendations}")
            limit = max_recommendations
        
        # 检查缓存
        if use_cache:
            cached_results = get_cached_job_recommendations(resume_id, config_id)
            if cached_results:
                # 如果缓存有效，直接返回（考虑limit限制）
                result = cached_results[:limit] if limit < len(cached_results) else cached_results
                logger.info(f"使用缓存返回简历 {resume_id} 的推荐职位，耗时: {time.time() - start_time:.3f}秒")
                return result
        
        # 使用向量搜索获取推荐
        vector_recommendations = []
        try:
            vector_recommendations = await get_vector_job_recommendations(db, resume_id, limit=int(limit * 1.5))
            logger.info(f"向量搜索为简历 {resume_id} 找到 {len(vector_recommendations)} 个推荐职位")
        except Exception as e:
            logger.error(f"向量搜索推荐职位时出错: {str(e)}", exc_info=True)
        
        # 检查LightFM模型是否就绪
        lightfm_recommendations = []
        if is_lightfm_ready():
            try:
                # 使用LightFM获取推荐
                lightfm_recommendations = await get_lightfm_job_recommendations(resume_id, db, limit=int(limit * 1.5))
                logger.info(f"LightFM为简历 {resume_id} 找到 {len(lightfm_recommendations)} 个推荐职位")
            except Exception as e:
                logger.error(f"使用LightFM推荐职位时出错: {str(e)}", exc_info=True)
        else:
            logger.warning("LightFM模型未就绪，只使用向量搜索进行推荐")
            # 如果LightFM不可用，调整向量搜索权重为1
            vector_weight = 1.0
            lightfm_weight = 0.0
        
        # 合并结果并计算最终分数
        merged_recommendations = {}
        
        # 检查向量搜索结果是否为空
        if not vector_recommendations and not lightfm_recommendations:
            logger.warning(f"没有找到推荐职位，简历ID: {resume_id}")
            return []
        
        # 处理向量搜索结果
        if vector_recommendations:
            for rec in vector_recommendations:
                job_id = rec.get("id")
                if not job_id:
                    logger.warning("推荐结果中存在没有ID的项，已跳过")
                    continue
                
                # 构建基本信息
                merged_recommendations[job_id] = {
                    "id": job_id,
                    "title": rec.get("title", ""),
                    "company": rec.get("company", ""),
                    "match_score": rec.get("match_score", 0) * vector_weight,
                    "algorithms": ["vector"]
                }
                
                # 如果需要详细信息，添加匹配技能等
                if include_details:
                    merged_recommendations[job_id]["match_details"] = {
                        "similarity": rec.get("similarity", 0),
                        "skill_score": rec.get("skill_score", 0),
                        "matched_skills": rec.get("matched_skills", [])
                    }
        
        # 处理LightFM结果
        if lightfm_recommendations:
            for rec in lightfm_recommendations:
                job_id = rec.get("id")
                if not job_id:
                    logger.warning("LightFM推荐结果中存在没有ID的项，已跳过")
                    continue
                    
                if job_id in merged_recommendations:
                    # 如果已存在，更新分数并添加算法
                    merged_recommendations[job_id]["match_score"] += rec.get("match_score", 0) * lightfm_weight
                    merged_recommendations[job_id]["algorithms"].append("lightfm")
                    if include_details and "match_details" in merged_recommendations[job_id]:
                        merged_recommendations[job_id]["match_details"]["lightfm_score"] = rec.get("match_score", 0)
                else:
                    # 如果不存在，添加新条目
                    merged_recommendations[job_id] = {
                        "id": job_id,
                        "title": rec.get("title", ""),
                        "company": rec.get("company", ""),
                        "match_score": rec.get("match_score", 0) * lightfm_weight,
                        "algorithms": ["lightfm"]
                    }
                    
                    if include_details:
                        merged_recommendations[job_id]["match_details"] = {
                            "lightfm_score": rec.get("match_score", 0)
                        }
        
        # 转换为列表，按匹配分数排序
        result = list(merged_recommendations.values())
        result.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 限制结果数量
        result = result[:limit]
        
        # 缓存结果
        if use_cache and result:
            # 缓存完整结果而不仅仅是limit限制后的结果
            cache_job_recommendations(resume_id, result, config_id)
        
        processing_time = time.time() - start_time
        logger.info(f"成功合并向量和LightFM推荐，共返回 {len(result)} 个结果，处理耗时: {processing_time:.3f}秒")
        return result
    except Exception as e:
        logger.error(f"获取推荐职位时出错: {str(e)}", exc_info=True)
        return []


async def get_recommended_resumes(
    db: Session,
    job_id: int,
    limit: int = None,
    include_details: bool = True,
    use_cache: bool = DEFAULT_CACHE_ENABLED
) -> List[Dict[str, Any]]:
    """
    获取推荐简历列表
    
    Args:
        db: 数据库会话
        job_id: 职位ID
        limit: 返回结果数量限制
        include_details: 是否包含详细信息
        use_cache: 是否使用缓存
        
    Returns:
        推荐简历列表
    """
    try:
        start_time = time.time()
        
        # 获取当前配置或使用默认值
        config = recommendation_config.get_active_config(db)
        if not config:
            logger.warning("找不到活跃的推荐配置，将创建默认配置")
            config = recommendation_config.create_default_config(db)
        
        # 如果仍没有配置，使用默认值
        if not config:
            logger.warning("无法创建默认配置，使用硬编码的默认值")
            max_recommendations = 10
            vector_weight = 0.6
            lightfm_weight = 0.4
            config_id = 0
        else:
            max_recommendations = config.max_recommendations
            vector_weight = config.vector_weight
            lightfm_weight = config.lightfm_weight
            config_id = config.id
            
            # 确保权重总和为1
            if abs(vector_weight + lightfm_weight - 1.0) > 0.001:
                logger.warning(f"向量权重({vector_weight})和LightFM权重({lightfm_weight})之和不为1，将进行归一化")
                total = vector_weight + lightfm_weight
                if total > 0:
                    vector_weight = vector_weight / total
                    lightfm_weight = lightfm_weight / total
                else:
                    # 如果总和为0或负数，设置默认值
                    vector_weight = 0.6
                    lightfm_weight = 0.4
                    logger.warning(f"权重总和异常，已重置为默认值：向量权重={vector_weight}，LightFM权重={lightfm_weight}")
        
        # 应用结果数量限制
        if limit is None:
            limit = max_recommendations
        elif limit <= 0:
            logger.warning(f"无效的结果数量限制: {limit}，将使用默认值: {max_recommendations}")
            limit = max_recommendations
            
        # 检查缓存
        if use_cache:
            cached_results = get_cached_resume_recommendations(job_id, config_id)
            if cached_results:
                # 如果缓存有效，直接返回（考虑limit限制）
                result = cached_results[:limit] if limit < len(cached_results) else cached_results
                logger.info(f"使用缓存返回职位 {job_id} 的推荐简历，耗时: {time.time() - start_time:.3f}秒")
                return result
        
        # 使用向量搜索获取推荐
        vector_recommendations = []
        try:
            vector_recommendations = await get_vector_resume_recommendations(db, job_id, limit=int(limit * 1.5))
            logger.info(f"向量搜索为职位 {job_id} 找到 {len(vector_recommendations)} 个推荐简历")
        except Exception as e:
            logger.error(f"向量搜索推荐简历时出错: {str(e)}", exc_info=True)
        
        # 检查LightFM模型是否就绪
        lightfm_recommendations = []
        if is_lightfm_ready():
            try:
                # 使用LightFM获取推荐
                lightfm_recommendations = await get_lightfm_resume_recommendations(job_id, db, limit=int(limit * 1.5))
                logger.info(f"LightFM为职位 {job_id} 找到 {len(lightfm_recommendations)} 个推荐简历")
            except Exception as e:
                logger.error(f"使用LightFM推荐简历时出错: {str(e)}", exc_info=True)
        else:
            logger.warning("LightFM模型未就绪，只使用向量搜索进行推荐")
            # 如果LightFM不可用，调整向量搜索权重为1
            vector_weight = 1.0
            lightfm_weight = 0.0
        
        # 合并结果并计算最终分数
        merged_recommendations = {}
        
        # 检查向量搜索结果是否为空
        if not vector_recommendations and not lightfm_recommendations:
            logger.warning(f"没有找到推荐简历，职位ID: {job_id}")
            return []
        
        # 处理向量搜索结果
        if vector_recommendations:
            for rec in vector_recommendations:
                resume_id = rec.get("id")
                if not resume_id:
                    logger.warning("推荐结果中存在没有ID的项，已跳过")
                    continue
                
                # 构建基本信息
                merged_recommendations[resume_id] = {
                    "id": resume_id,
                    "title": rec.get("title", ""),
                    "user": rec.get("user", {}),
                    "match_score": rec.get("match_score", 0) * vector_weight,
                    "algorithms": ["vector"]
                }
                
                # 如果需要详细信息，添加匹配技能等
                if include_details:
                    merged_recommendations[resume_id]["match_details"] = {
                        "similarity": rec.get("similarity", 0),
                        "skill_score": rec.get("skill_score", 0),
                        "matched_skills": rec.get("matched_skills", [])
                    }
        
        # 处理LightFM结果
        if lightfm_recommendations:
            for rec in lightfm_recommendations:
                resume_id = rec.get("id")
                if not resume_id:
                    logger.warning("LightFM推荐结果中存在没有ID的项，已跳过")
                    continue
                
                if resume_id in merged_recommendations:
                    # 如果已存在，更新分数并添加算法
                    merged_recommendations[resume_id]["match_score"] += rec.get("match_score", 0) * lightfm_weight
                    merged_recommendations[resume_id]["algorithms"].append("lightfm")
                    if include_details and "match_details" in merged_recommendations[resume_id]:
                        merged_recommendations[resume_id]["match_details"]["lightfm_score"] = rec.get("match_score", 0)
                else:
                    # 如果不存在，添加新条目
                    merged_recommendations[resume_id] = {
                        "id": resume_id,
                        "title": rec.get("title", ""),
                        "user": rec.get("user", {}),
                        "match_score": rec.get("match_score", 0) * lightfm_weight,
                        "algorithms": ["lightfm"]
                    }
                    
                    if include_details:
                        merged_recommendations[resume_id]["match_details"] = {
                            "lightfm_score": rec.get("match_score", 0)
                        }
        
        # 转换为列表，按匹配分数排序
        result = list(merged_recommendations.values())
        result.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 限制结果数量
        result = result[:limit]
        
        # 缓存结果
        if use_cache and result:
            # 缓存完整结果
            cache_resume_recommendations(job_id, result, config_id)
        
        processing_time = time.time() - start_time
        logger.info(f"成功合并向量和LightFM推荐，共返回 {len(result)} 个结果，处理耗时: {processing_time:.3f}秒")
        return result
    except Exception as e:
        logger.error(f"获取推荐简历时出错: {str(e)}", exc_info=True)
        return [] 