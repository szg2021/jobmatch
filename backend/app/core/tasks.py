import logging
import traceback
from datetime import datetime
import asyncio
import time
import re
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.db.session import SessionLocal
from app.services.lightfm_recommendation_service import prepare_and_train_lightfm, force_reload_model
from app.services.recommendation_service import initialize_vector_search, schedule_cache_cleanup
from app.services.feedback_service import feedback_service
from app.crud.crud_recommendation_config import recommendation_config

logger = logging.getLogger("app.core.tasks")

# 全局变量用于跟踪状态
training_in_progress = False
last_trained_time = None
vector_search_initialized = False
task_locks = {
    "train_lightfm": False,
    "initialize_search": False,
    "clean_cache": False,
    "process_feedback": False
}
task_last_run = {
    "train_lightfm": None,
    "initialize_search": None,
    "clean_cache": None,
    "process_feedback": None
}
task_failures = {
    "train_lightfm": 0,
    "initialize_search": 0,
    "clean_cache": 0,
    "process_feedback": 0
}

MAX_FAILURES = 3  # 最大连续失败次数
RETRY_DELAY = 60  # 失败后重试延迟（秒）
CACHE_CLEANUP_INTERVAL = 3600  # 缓存清理间隔（秒）
FEEDBACK_PROCESS_INTERVAL = 86400  # 反馈处理间隔（秒）

async def initialize_search_services(db: Session = None):
    """初始化搜索服务"""
    global vector_search_initialized, task_locks, task_last_run, task_failures
    
    # 检查锁状态
    if task_locks["initialize_search"]:
        logger.info("向量搜索服务初始化任务已在进行中")
        return False
        
    # 设置锁
    task_locks["initialize_search"] = True
    task_last_run["initialize_search"] = datetime.now()
    
    try:
        if vector_search_initialized:
            logger.info("向量搜索服务已初始化")
            return True
        
        logger.info("开始初始化向量搜索服务")
        
        # 如果未提供数据库会话，创建一个新的
        if db is None:
            db = SessionLocal()
            should_close_db = True
        else:
            should_close_db = False
        
        try:
            # 初始化向量搜索
            success = await initialize_vector_search(db)
            if success:
                vector_search_initialized = True
                task_failures["initialize_search"] = 0  # 重置失败计数
                logger.info("向量搜索服务初始化成功")
                return True
            else:
                task_failures["initialize_search"] += 1
                logger.error(f"向量搜索服务初始化失败，这是第 {task_failures['initialize_search']} 次失败")
                return False
        finally:
            if should_close_db and db:
                db.close()
    except Exception as e:
        task_failures["initialize_search"] += 1
        error_stack = traceback.format_exc()
        logger.error(f"初始化搜索服务时出错: {str(e)}\n{error_stack}")
        return False
    finally:
        # 释放锁
        task_locks["initialize_search"] = False

async def train_lightfm_model():
    """训练LightFM推荐模型的任务"""
    global training_in_progress, last_trained_time, task_locks, task_last_run, task_failures
    
    # 检查锁状态
    if task_locks["train_lightfm"]:
        logger.info("另一个训练任务已在进行中，跳过本次训练")
        return False
    
    # 设置锁
    task_locks["train_lightfm"] = True
    task_last_run["train_lightfm"] = datetime.now()
    training_in_progress = True
    
    logger.info("开始训练LightFM模型")
    
    db = None
    try:
        # 获取数据库会话
        db = SessionLocal()
        
        # 获取配置
        config = recommendation_config.get_config_for_training(db)
        
        # 训练模型
        success = await prepare_and_train_lightfm(db, config)
        
        if success:
            # 更新最后训练时间
            last_trained_time = datetime.now()
            
            # 更新配置中的最后训练时间
            active_config = recommendation_config.get_active_config(db)
            if active_config:
                active_config.last_trained = last_trained_time
                db.add(active_config)
                db.commit()
                
            # 重置失败计数
            task_failures["train_lightfm"] = 0
                
            logger.info(f"LightFM模型训练成功完成，时间: {last_trained_time}")
            
            # 强制重新加载模型，确保使用最新的模型
            force_reload_model()
            
            return True
        else:
            task_failures["train_lightfm"] += 1
            logger.error(f"LightFM模型训练失败，这是第 {task_failures['train_lightfm']} 次失败")
            return False
    except Exception as e:
        task_failures["train_lightfm"] += 1
        error_stack = traceback.format_exc()
        logger.error(f"训练LightFM模型时出错: {str(e)}\n{error_stack}")
        return False
    finally:
        if db:
            db.close()
        # 释放锁
        task_locks["train_lightfm"] = False
        training_in_progress = False

async def clean_recommendation_cache():
    """清理推荐缓存的任务"""
    global task_locks, task_last_run, task_failures
    
    # 检查锁状态
    if task_locks["clean_cache"]:
        logger.debug("缓存清理任务已在进行中")
        return False
    
    # 设置锁
    task_locks["clean_cache"] = True
    task_last_run["clean_cache"] = datetime.now()
    
    try:
        logger.info("开始清理推荐缓存")
        start_time = time.time()
        
        # 执行缓存清理
        await schedule_cache_cleanup()
        
        processing_time = time.time() - start_time
        logger.info(f"推荐缓存清理完成，耗时: {processing_time:.3f}秒")
        
        # 重置失败计数
        task_failures["clean_cache"] = 0
        return True
    except Exception as e:
        task_failures["clean_cache"] += 1
        error_stack = traceback.format_exc()
        logger.error(f"清理推荐缓存时出错: {str(e)}\n{error_stack}")
        return False
    finally:
        # 释放锁
        task_locks["clean_cache"] = False

async def process_user_feedback():
    """处理用户反馈并计算指标的任务"""
    global task_locks, task_last_run, task_failures
    
    # 检查锁状态
    if task_locks["process_feedback"]:
        logger.debug("反馈处理任务已在进行中")
        return False
    
    # 设置锁
    task_locks["process_feedback"] = True
    task_last_run["process_feedback"] = datetime.now()
    
    db = None
    try:
        logger.info("开始处理用户反馈")
        start_time = time.time()
        
        # 获取数据库会话
        db = SessionLocal()
        
        # 清理反馈缓存
        feedback_service.clean_feedback_cache()
        
        # 计算反馈指标
        metrics = await feedback_service.compute_feedback_metrics(db)
        
        processing_time = time.time() - start_time
        logger.info(f"用户反馈处理完成，耗时: {processing_time:.3f}秒")
        
        # 重置失败计数
        task_failures["process_feedback"] = 0
        return True
    except Exception as e:
        task_failures["process_feedback"] += 1
        error_stack = traceback.format_exc()
        logger.error(f"处理用户反馈时出错: {str(e)}\n{error_stack}")
        return False
    finally:
        if db:
            db.close()
        # 释放锁
        task_locks["process_feedback"] = False

def parse_cron(cron_str: str) -> bool:
    """
    检查当前时间是否匹配cron表达式
    简化版cron解析，仅支持分钟、小时、日、月、星期格式
    """
    try:
        if not cron_str or not isinstance(cron_str, str):
            return False
            
        parts = cron_str.split()
        if len(parts) != 5:
            logger.error(f"无效的cron表达式: {cron_str}")
            return False
            
        now = datetime.now()
        minute, hour, day, month, weekday = parts
        
        # 检查分钟
        if minute != "*" and not _check_cron_match(minute, now.minute):
            return False
            
        # 检查小时
        if hour != "*" and not _check_cron_match(hour, now.hour):
            return False
            
        # 检查日期
        if day != "*" and not _check_cron_match(day, now.day):
            return False
            
        # 检查月份
        if month != "*" and not _check_cron_match(month, now.month):
            return False
            
        # 检查星期几 (0-6, 0是周日)
        if weekday != "*":
            # 正确处理星期
            python_weekday = now.weekday()  # 0是周一
            cron_weekday = (python_weekday + 1) % 7  # 转换为cron格式，0是周日
            
            if not _check_cron_match(weekday, cron_weekday):
                return False
                
        return True
    except Exception as e:
        logger.error(f"解析cron表达式时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def _check_cron_match(cron_part: str, current_value: int) -> bool:
    """检查cron表达式的一部分是否匹配当前值"""
    try:
        # 处理逗号分隔的多值
        if "," in cron_part:
            values = [int(x) for x in cron_part.split(",")]
            return current_value in values
        
        # 处理范围 (例如 1-5)
        elif "-" in cron_part:
            start, end = map(int, cron_part.split("-"))
            return start <= current_value <= end
        
        # 处理步长 (例如 */5)
        elif "/" in cron_part:
            parts = cron_part.split("/")
            if parts[0] == "*":
                return current_value % int(parts[1]) == 0
            else:
                # 不支持更复杂的步长表达式
                return False
        
        # 处理单个数值
        else:
            return int(cron_part) == current_value
    except ValueError as e:
        logger.error(f"解析cron表达式部分时出错: {cron_part}, 错误: {str(e)}")
        return False

async def schedule_periodic_tasks():
    """定期运行任务的调度器"""
    logger.info("启动定期任务调度器")
    
    # 记录缓存清理和反馈处理的上次运行时间
    last_cache_cleanup = None
    last_feedback_process = None
    
    while True:
        try:
            # 等待1分钟再检查
            await asyncio.sleep(60)
            
            # 检查是否需要初始化搜索服务（如果尚未初始化）
            if not vector_search_initialized:
                await initialize_search_services()
            
            # 检查是否需要重试失败的任务
            for task_name, failures in task_failures.items():
                if failures >= MAX_FAILURES:
                    logger.warning(f"任务 {task_name} 已连续失败 {failures} 次，将暂停该任务")
                elif failures > 0:
                    last_run = task_last_run.get(task_name)
                    if last_run:
                        elapsed = (datetime.now() - last_run).total_seconds()
                        if elapsed > RETRY_DELAY:
                            logger.info(f"尝试重新执行先前失败的任务: {task_name}")
                            if task_name == "train_lightfm":
                                await train_lightfm_model()
                            elif task_name == "initialize_search":
                                await initialize_search_services()
                            elif task_name == "clean_cache":
                                await clean_recommendation_cache()
                            elif task_name == "process_feedback":
                                await process_user_feedback()
            
            # 检查是否需要清理缓存
            now = datetime.now()
            if not last_cache_cleanup or (now - last_cache_cleanup).total_seconds() >= CACHE_CLEANUP_INTERVAL:
                logger.info("触发定期缓存清理")
                success = await clean_recommendation_cache()
                if success:
                    last_cache_cleanup = now
            
            # 检查是否需要处理反馈
            if not last_feedback_process or (now - last_feedback_process).total_seconds() >= FEEDBACK_PROCESS_INTERVAL:
                logger.info("触发定期反馈处理")
                success = await process_user_feedback()
                if success:
                    last_feedback_process = now
            
            # 检查是否需要训练模型
            db = None
            try:
                db = SessionLocal()
                
                # 获取活跃配置
                config = recommendation_config.get_active_config(db)
                if not config:
                    logger.debug("没有活跃配置，无法检查训练计划")
                    continue
                
                # 检查cron表达式
                if config.train_schedule and parse_cron(config.train_schedule):
                    logger.info(f"根据计划 '{config.train_schedule}' 触发模型训练")
                    await train_lightfm_model()
            except Exception as e:
                logger.error(f"检查定期任务时出错: {str(e)}")
                logger.error(traceback.format_exc())
            finally:
                if db:
                    db.close()
        except Exception as e:
            logger.error(f"任务调度器出错: {str(e)}")
            logger.error(traceback.format_exc())
            # 出错后暂停一下再继续
            await asyncio.sleep(60)

async def check_startup_training():
    """检查是否需要在启动时训练模型"""
    # 等待应用完全初始化
    await asyncio.sleep(15)
    
    db = None
    try:
        logger.info("检查是否需要在启动时训练模型")
        db = SessionLocal()
        
        # 初始化向量搜索服务
        await initialize_search_services(db)
        
        # 获取活跃配置
        config = recommendation_config.get_active_config(db)
        
        # 如果没有配置，创建默认配置
        if not config:
            config = recommendation_config.create_default_config(db)
            if not config:
                logger.warning("无法创建默认配置")
                return
        
        # 检查是否需要在启动时训练
        if config.train_on_startup:
            logger.info("根据配置在应用启动时训练模型")
            await train_lightfm_model()
        else:
            logger.info("配置不要求在启动时训练模型")
            
        # 在启动时清理一次缓存
        await clean_recommendation_cache()
    except Exception as e:
        logger.error(f"检查启动训练时出错: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        if db:
            db.close()

def start_background_tasks():
    """启动后台任务"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 启动定期任务调度器
    loop.create_task(schedule_periodic_tasks())
    
    # 检查是否需要在启动时训练
    loop.create_task(check_startup_training())
    
    # 运行事件循环
    loop.run_forever() 