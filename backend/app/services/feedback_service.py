import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models.feedback import RecommendationFeedback, FeedbackType, FeedbackMetrics
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.crud.crud_recommendation_config import recommendation_config

logger = logging.getLogger(__name__)

class FeedbackService:
    """处理用户反馈并改进推荐系统"""
    
    def __init__(self):
        self.positive_feedback_types = {
            FeedbackType.RELEVANT,
            FeedbackType.BOOKMARK,
            FeedbackType.APPLIED
        }
        self.negative_feedback_types = {
            FeedbackType.NOT_RELEVANT,
            FeedbackType.SKIPPED
        }
        self.explicit_feedback_type = FeedbackType.EXPLICIT
        self.viewed_feedback_type = FeedbackType.VIEWED
        
        # 正面反馈的权重
        self.feedback_weights = {
            FeedbackType.RELEVANT: 1.0,
            FeedbackType.BOOKMARK: 0.8,
            FeedbackType.APPLIED: 1.0,
            FeedbackType.NOT_RELEVANT: -1.0,
            FeedbackType.SKIPPED: -0.5,
            FeedbackType.VIEWED: 0.1,
            FeedbackType.EXPLICIT: 1.0  # 显式评分的权重由评分值确定
        }
        
        # 缓存最近的正面反馈
        self.recent_positive_feedback = {}  # {user_id: {job_id: [feedback1, feedback2, ...], ...}, ...}
        self.recent_negative_feedback = {}  # 结构同上
        
        # 反馈缓存的过期时间（天）
        self.feedback_cache_ttl = 7 
    
    async def record_feedback(
        self, 
        db: Session, 
        user_id: int, 
        feedback_type: str, 
        job_id: Optional[int] = None, 
        resume_id: Optional[int] = None,
        rating: Optional[float] = None,
        comment: Optional[str] = None,
        algorithm: Optional[str] = None
    ) -> RecommendationFeedback:
        """记录用户反馈"""
        try:
            # 创建反馈记录
            feedback = RecommendationFeedback(
                user_id=user_id,
                job_id=job_id,
                resume_id=resume_id,
                feedback_type=feedback_type,
                rating=rating,
                comment=comment,
                algorithm=algorithm
            )
            
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            
            # 更新缓存
            if feedback_type in self.positive_feedback_types:
                self._add_to_positive_feedback_cache(user_id, job_id, resume_id, feedback)
            elif feedback_type in self.negative_feedback_types:
                self._add_to_negative_feedback_cache(user_id, job_id, resume_id, feedback)
            
            logger.info(f"已记录用户 {user_id} 的反馈: {feedback_type}, 职位: {job_id}, 简历: {resume_id}")
            return feedback
        except Exception as e:
            db.rollback()
            logger.error(f"记录反馈时出错: {str(e)}", exc_info=True)
            raise
    
    def _add_to_positive_feedback_cache(self, user_id: int, job_id: Optional[int], resume_id: Optional[int], feedback: RecommendationFeedback):
        """添加到正面反馈缓存"""
        if user_id not in self.recent_positive_feedback:
            self.recent_positive_feedback[user_id] = {}
        
        if job_id:
            if 'jobs' not in self.recent_positive_feedback[user_id]:
                self.recent_positive_feedback[user_id]['jobs'] = {}
            
            if job_id not in self.recent_positive_feedback[user_id]['jobs']:
                self.recent_positive_feedback[user_id]['jobs'][job_id] = []
            
            self.recent_positive_feedback[user_id]['jobs'][job_id].append({
                'feedback_id': feedback.id,
                'feedback_type': feedback.feedback_type,
                'timestamp': datetime.now()
            })
        
        if resume_id:
            if 'resumes' not in self.recent_positive_feedback[user_id]:
                self.recent_positive_feedback[user_id]['resumes'] = {}
            
            if resume_id not in self.recent_positive_feedback[user_id]['resumes']:
                self.recent_positive_feedback[user_id]['resumes'][resume_id] = []
            
            self.recent_positive_feedback[user_id]['resumes'][resume_id].append({
                'feedback_id': feedback.id,
                'feedback_type': feedback.feedback_type,
                'timestamp': datetime.now()
            })
    
    def _add_to_negative_feedback_cache(self, user_id: int, job_id: Optional[int], resume_id: Optional[int], feedback: RecommendationFeedback):
        """添加到负面反馈缓存"""
        if user_id not in self.recent_negative_feedback:
            self.recent_negative_feedback[user_id] = {}
        
        if job_id:
            if 'jobs' not in self.recent_negative_feedback[user_id]:
                self.recent_negative_feedback[user_id]['jobs'] = {}
            
            if job_id not in self.recent_negative_feedback[user_id]['jobs']:
                self.recent_negative_feedback[user_id]['jobs'][job_id] = []
            
            self.recent_negative_feedback[user_id]['jobs'][job_id].append({
                'feedback_id': feedback.id,
                'feedback_type': feedback.feedback_type,
                'timestamp': datetime.now()
            })
        
        if resume_id:
            if 'resumes' not in self.recent_negative_feedback[user_id]:
                self.recent_negative_feedback[user_id]['resumes'] = {}
            
            if resume_id not in self.recent_negative_feedback[user_id]['resumes']:
                self.recent_negative_feedback[user_id]['resumes'][resume_id] = []
            
            self.recent_negative_feedback[user_id]['resumes'][resume_id].append({
                'feedback_id': feedback.id,
                'feedback_type': feedback.feedback_type,
                'timestamp': datetime.now()
            })
    
    def clean_feedback_cache(self):
        """清理过期的反馈缓存"""
        expiry_date = datetime.now() - timedelta(days=self.feedback_cache_ttl)
        users_to_remove = []
        
        # 清理正面反馈缓存
        for user_id, user_data in self.recent_positive_feedback.items():
            if 'jobs' in user_data:
                jobs_to_remove = []
                for job_id, feedbacks in user_data['jobs'].items():
                    # 过滤出未过期的反馈
                    valid_feedbacks = [f for f in feedbacks if f['timestamp'] > expiry_date]
                    if valid_feedbacks:
                        user_data['jobs'][job_id] = valid_feedbacks
                    else:
                        jobs_to_remove.append(job_id)
                
                # 移除空的job entries
                for job_id in jobs_to_remove:
                    del user_data['jobs'][job_id]
            
            if 'resumes' in user_data:
                resumes_to_remove = []
                for resume_id, feedbacks in user_data['resumes'].items():
                    valid_feedbacks = [f for f in feedbacks if f['timestamp'] > expiry_date]
                    if valid_feedbacks:
                        user_data['resumes'][resume_id] = valid_feedbacks
                    else:
                        resumes_to_remove.append(resume_id)
                
                # 移除空的resume entries
                for resume_id in resumes_to_remove:
                    del user_data['resumes'][resume_id]
            
            # 检查用户是否有任何反馈
            if (not user_data.get('jobs') or not user_data['jobs']) and \
               (not user_data.get('resumes') or not user_data['resumes']):
                users_to_remove.append(user_id)
        
        # 移除空的用户
        for user_id in users_to_remove:
            del self.recent_positive_feedback[user_id]
        
        # 对负面反馈执行相同的清理
        users_to_remove = []
        for user_id, user_data in self.recent_negative_feedback.items():
            # ... 相同的清理逻辑 ...
            if 'jobs' in user_data:
                jobs_to_remove = []
                for job_id, feedbacks in user_data['jobs'].items():
                    valid_feedbacks = [f for f in feedbacks if f['timestamp'] > expiry_date]
                    if valid_feedbacks:
                        user_data['jobs'][job_id] = valid_feedbacks
                    else:
                        jobs_to_remove.append(job_id)
                
                for job_id in jobs_to_remove:
                    del user_data['jobs'][job_id]
            
            if 'resumes' in user_data:
                resumes_to_remove = []
                for resume_id, feedbacks in user_data['resumes'].items():
                    valid_feedbacks = [f for f in feedbacks if f['timestamp'] > expiry_date]
                    if valid_feedbacks:
                        user_data['resumes'][resume_id] = valid_feedbacks
                    else:
                        resumes_to_remove.append(resume_id)
                
                for resume_id in resumes_to_remove:
                    del user_data['resumes'][resume_id]
            
            if (not user_data.get('jobs') or not user_data['jobs']) and \
               (not user_data.get('resumes') or not user_data['resumes']):
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.recent_negative_feedback[user_id]
        
        logger.info("反馈缓存清理完成")
    
    async def get_feedback_for_user(
        self, 
        db: Session, 
        user_id: int, 
        feedback_type: Optional[str] = None,
        days: Optional[int] = 30
    ) -> List[RecommendationFeedback]:
        """获取用户的反馈历史"""
        query = db.query(RecommendationFeedback).filter(RecommendationFeedback.user_id == user_id)
        
        if feedback_type:
            query = query.filter(RecommendationFeedback.feedback_type == feedback_type)
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(RecommendationFeedback.created_at >= cutoff_date)
        
        return query.order_by(desc(RecommendationFeedback.created_at)).all()
    
    async def apply_feedback_to_recommendations(
        self, 
        user_id: int,
        recommendations: List[Dict[str, Any]],
        is_job_recommendations: bool = True
    ) -> List[Dict[str, Any]]:
        """根据用户反馈调整推荐结果的排序"""
        # 如果无推荐或无用户ID，直接返回
        if not recommendations or not user_id:
            return recommendations
        
        # 查找用户的反馈缓存
        positive_cache = self.recent_positive_feedback.get(user_id, {})
        negative_cache = self.recent_negative_feedback.get(user_id, {})
        
        # 确定要查找哪种类型的反馈（职位或简历）
        item_type = 'jobs' if is_job_recommendations else 'resumes'
        
        # 如果没有任何反馈，直接返回原始推荐
        if (not positive_cache.get(item_type) and not negative_cache.get(item_type)):
            return recommendations
        
        adjusted_recommendations = []
        
        for recommendation in recommendations:
            item_id = recommendation.get('id')
            if not item_id:
                adjusted_recommendations.append(recommendation)
                continue
            
            # 获取原始匹配分数
            match_score = recommendation.get('match_score', 0.0)
            
            # 应用正面反馈
            positive_feedbacks = positive_cache.get(item_type, {}).get(item_id, [])
            for feedback in positive_feedbacks:
                feedback_type = feedback.get('feedback_type')
                if feedback_type in self.feedback_weights:
                    weight = self.feedback_weights[feedback_type]
                    # 根据反馈提升分数，但限制最大值
                    match_score = min(match_score + weight * 0.1, 1.0)
            
            # 应用负面反馈
            negative_feedbacks = negative_cache.get(item_type, {}).get(item_id, [])
            for feedback in negative_feedbacks:
                feedback_type = feedback.get('feedback_type')
                if feedback_type in self.feedback_weights:
                    weight = self.feedback_weights[feedback_type]
                    # 根据反馈降低分数，但限制最小值
                    match_score = max(match_score + weight * 0.1, 0.0)
            
            # 更新分数并添加到结果
            adjusted_recommendation = dict(recommendation)
            adjusted_recommendation['match_score'] = match_score
            adjusted_recommendation['adjusted_by_feedback'] = True
            adjusted_recommendations.append(adjusted_recommendation)
        
        # 重新按匹配分数排序
        adjusted_recommendations.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return adjusted_recommendations
    
    async def compute_feedback_metrics(self, db: Session) -> Dict[str, Any]:
        """计算反馈指标来评估推荐系统性能"""
        try:
            # 获取活动配置
            config = recommendation_config.get_active_config(db)
            config_id = config.id if config else None
            
            # 计算总反馈数
            total_feedback = db.query(func.count(RecommendationFeedback.id)).scalar()
            
            # 计算过去30天的反馈数
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_feedback = db.query(func.count(RecommendationFeedback.id))\
                .filter(RecommendationFeedback.created_at >= cutoff_date).scalar()
            
            # 计算每种反馈类型的数量
            feedback_counts = {}
            for feedback_type in FeedbackType:
                count = db.query(func.count(RecommendationFeedback.id))\
                    .filter(RecommendationFeedback.feedback_type == feedback_type)\
                    .filter(RecommendationFeedback.created_at >= cutoff_date).scalar()
                feedback_counts[feedback_type] = count
            
            # 计算每种算法的反馈统计
            algorithm_metrics = {}
            algorithms = db.query(RecommendationFeedback.algorithm)\
                .filter(RecommendationFeedback.algorithm.isnot(None))\
                .distinct().all()
            
            for alg in algorithms:
                algorithm = alg[0]
                
                # 跳过空算法名
                if not algorithm:
                    continue
                
                # 计算总反馈数
                total = db.query(func.count(RecommendationFeedback.id))\
                    .filter(RecommendationFeedback.algorithm == algorithm)\
                    .filter(RecommendationFeedback.created_at >= cutoff_date).scalar()
                
                # 计算正面反馈数
                positive = db.query(func.count(RecommendationFeedback.id))\
                    .filter(RecommendationFeedback.algorithm == algorithm)\
                    .filter(RecommendationFeedback.feedback_type.in_([t.value for t in self.positive_feedback_types]))\
                    .filter(RecommendationFeedback.created_at >= cutoff_date).scalar()
                
                # 计算负面反馈数
                negative = db.query(func.count(RecommendationFeedback.id))\
                    .filter(RecommendationFeedback.algorithm == algorithm)\
                    .filter(RecommendationFeedback.feedback_type.in_([t.value for t in self.negative_feedback_types]))\
                    .filter(RecommendationFeedback.created_at >= cutoff_date).scalar()
                
                # 计算显式评分平均值
                avg_rating = db.query(func.avg(RecommendationFeedback.rating))\
                    .filter(RecommendationFeedback.algorithm == algorithm)\
                    .filter(RecommendationFeedback.feedback_type == self.explicit_feedback_type.value)\
                    .filter(RecommendationFeedback.created_at >= cutoff_date).scalar()
                
                algorithm_metrics[algorithm] = {
                    'total_feedback': total,
                    'positive_feedback': positive,
                    'negative_feedback': negative,
                    'positive_ratio': positive / total if total > 0 else 0,
                    'negative_ratio': negative / total if total > 0 else 0,
                    'average_rating': float(avg_rating) if avg_rating else 0
                }
                
                # 保存到数据库
                for metric_name, value in algorithm_metrics[algorithm].items():
                    if isinstance(value, (int, float)):
                        metric = FeedbackMetrics(
                            algorithm=algorithm,
                            metric_type=metric_name,
                            value=float(value),
                            config_id=config_id,
                            details=json.dumps({'period': '30_days'})
                        )
                        db.add(metric)
            
            # 保存汇总指标
            overall_positive = sum(m['positive_feedback'] for m in algorithm_metrics.values())
            overall_negative = sum(m['negative_feedback'] for m in algorithm_metrics.values())
            overall_total = sum(m['total_feedback'] for m in algorithm_metrics.values())
            
            overall_metrics = {
                'total_feedback': overall_total,
                'positive_feedback': overall_positive,
                'negative_feedback': overall_negative,
                'positive_ratio': overall_positive / overall_total if overall_total > 0 else 0,
                'negative_ratio': overall_negative / overall_total if overall_total > 0 else 0
            }
            
            # 保存到数据库
            for metric_name, value in overall_metrics.items():
                metric = FeedbackMetrics(
                    algorithm='overall',
                    metric_type=metric_name,
                    value=float(value),
                    config_id=config_id,
                    details=json.dumps({'period': '30_days'})
                )
                db.add(metric)
            
            db.commit()
            
            # 返回计算的指标
            return {
                'summary': {
                    'total_feedback': total_feedback,
                    'recent_feedback': recent_feedback,
                    'feedback_by_type': feedback_counts
                },
                'algorithm_metrics': algorithm_metrics,
                'overall': overall_metrics
            }
        except Exception as e:
            db.rollback()
            logger.error(f"计算反馈指标时出错: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'summary': {},
                'algorithm_metrics': {},
                'overall': {}
            }

# 创建全局服务实例
feedback_service = FeedbackService() 