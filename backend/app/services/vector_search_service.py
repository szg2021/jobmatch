import logging
import numpy as np
import time
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User

logger = logging.getLogger(__name__)

class VectorSearchService:
    """向量搜索服务，用于简历和职位的文本相似度搜索"""
    
    def __init__(self):
        self.job_vectorizer = TfidfVectorizer(max_features=2000, stop_words='english')
        self.resume_vectorizer = TfidfVectorizer(max_features=2000, stop_words='english')
        self.job_vectors = None
        self.resume_vectors = None
        self.job_ids = []
        self.resume_ids = []
        self.initialized = False
        
        # 增量更新相关
        self.job_last_updated = {}  # 职位最后更新时间: {job_id: timestamp}
        self.resume_last_updated = {}  # 简历最后更新时间: {resume_id: timestamp}
        self.last_full_index = None  # 最后一次全量索引时间
        self.pending_job_updates = set()  # 等待更新的职位ID
        self.pending_resume_updates = set()  # 等待更新的简历ID
        self.max_pending_updates = 50  # 最大挂起更新数量，超过此值触发批量更新
        self.update_in_progress = False  # 是否正在进行批量更新
    
    async def initialize(self, db: Session, force_full: bool = False) -> bool:
        """初始化向量索引
        
        Args:
            db: 数据库会话
            force_full: 是否强制执行全量索引
        """
        try:
            # 如果已初始化且非强制全量索引，则可以跳过
            if self.initialized and not force_full:
                logger.info("向量搜索索引已初始化，跳过初始化步骤")
                return True
                
            logger.info("开始初始化向量搜索索引")
            start_time = time.time()
            
            # 获取所有职位
            jobs = db.query(Job).all()
            if not jobs:
                logger.warning("没有找到职位数据，无法创建向量索引")
                return False
            
            # 获取所有简历
            resumes = db.query(Resume).all()
            if not resumes:
                logger.warning("没有找到简历数据，无法创建向量索引")
                return False
            
            # 提取职位文本
            job_texts = []
            self.job_ids = []
            for job in jobs:
                job_text = f"{job.title} {job.description} {job.requirements or ''}"
                job_texts.append(job_text)
                self.job_ids.append(job.id)
                self.job_last_updated[job.id] = datetime.now()
            
            # 提取简历文本
            resume_texts = []
            self.resume_ids = []
            for resume in resumes:
                resume_text = f"{resume.title} {resume.summary or ''} {resume.skills or ''} {resume.experience or ''}"
                resume_texts.append(resume_text)
                self.resume_ids.append(resume.id)
                self.resume_last_updated[resume.id] = datetime.now()
            
            # 创建向量
            self.job_vectors = self.job_vectorizer.fit_transform(job_texts)
            self.resume_vectors = self.resume_vectorizer.fit_transform(resume_texts)
            
            # 更新索引状态
            self.initialized = True
            self.last_full_index = datetime.now()
            self.pending_job_updates.clear()
            self.pending_resume_updates.clear()
            
            processing_time = time.time() - start_time
            logger.info(f"向量索引初始化完成。已索引 {len(self.job_ids)} 个职位和 {len(self.resume_ids)} 个简历，耗时: {processing_time:.3f}秒")
            return True
        except Exception as e:
            logger.error(f"初始化向量索引时出错: {str(e)}", exc_info=True)
            return False
    
    def _extract_skills(self, text: str) -> List[str]:
        """从文本中提取技能关键词"""
        # 简化实现，实际应使用更复杂的技能提取算法
        # 这里假设所有大写单词或包含特定前缀的词是技能
        words = text.split()
        skills = []
        skill_prefixes = ["python", "java", "c++", "javascript", "react", "angular", "vue", 
                         "node", "sql", "nosql", "aws", "azure", "docker", "kubernetes"]
        
        for word in words:
            word = word.lower().strip(",.;:!?()-")
            if word.isupper() or any(word.startswith(prefix) for prefix in skill_prefixes):
                skills.append(word)
        
        return list(set(skills))
    
    def _get_skill_match_score(self, job_text: str, resume_text: str) -> Tuple[float, List[str]]:
        """计算技能匹配分数和匹配的技能列表"""
        job_skills = self._extract_skills(job_text)
        resume_skills = self._extract_skills(resume_text)
        
        if not job_skills or not resume_skills:
            return 0.0, []
        
        matched_skills = [skill for skill in resume_skills if skill in job_skills]
        if not matched_skills:
            return 0.0, []
        
        # 计算匹配率
        match_ratio = len(matched_skills) / len(job_skills) if job_skills else 0
        return match_ratio, matched_skills
    
    async def update_job_vector(self, db: Session, job_id: int) -> bool:
        """更新单个职位的向量表示"""
        try:
            # 如果未初始化，尝试初始化
            if not self.initialized:
                success = await self.initialize(db)
                if not success:
                    logger.error("向量索引未初始化，无法更新职位向量")
                    return False
            
            # 获取职位
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.warning(f"找不到ID为 {job_id} 的职位")
                return False
            
            # 提取文本
            job_text = f"{job.title} {job.description} {job.requirements or ''}"
            
            # 检查职位是否已在索引中
            if job_id in self.job_ids:
                # 更新现有向量
                idx = self.job_ids.index(job_id)
                job_vector = self.job_vectorizer.transform([job_text])
                self.job_vectors[idx] = job_vector
            else:
                # 添加新向量
                job_vector = self.job_vectorizer.transform([job_text])
                self.job_vectors = np.vstack([self.job_vectors, job_vector]) if self.job_vectors is not None else job_vector
                self.job_ids.append(job_id)
            
            # 更新时间戳
            self.job_last_updated[job_id] = datetime.now()
            
            # 从待更新列表中移除
            if job_id in self.pending_job_updates:
                self.pending_job_updates.remove(job_id)
                
            logger.info(f"已更新职位 {job_id} 的向量表示")
            return True
        except Exception as e:
            logger.error(f"更新职位向量时出错: {str(e)}", exc_info=True)
            # 添加到待更新列表
            self.pending_job_updates.add(job_id)
            return False
    
    async def update_resume_vector(self, db: Session, resume_id: int) -> bool:
        """更新单个简历的向量表示"""
        try:
            # 如果未初始化，尝试初始化
            if not self.initialized:
                success = await self.initialize(db)
                if not success:
                    logger.error("向量索引未初始化，无法更新简历向量")
                    return False
            
            # 获取简历
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                logger.warning(f"找不到ID为 {resume_id} 的简历")
                return False
            
            # 提取文本
            resume_text = f"{resume.title} {resume.summary or ''} {resume.skills or ''} {resume.experience or ''}"
            
            # 检查简历是否已在索引中
            if resume_id in self.resume_ids:
                # 更新现有向量
                idx = self.resume_ids.index(resume_id)
                resume_vector = self.resume_vectorizer.transform([resume_text])
                self.resume_vectors[idx] = resume_vector
            else:
                # 添加新向量
                resume_vector = self.resume_vectorizer.transform([resume_text])
                self.resume_vectors = np.vstack([self.resume_vectors, resume_vector]) if self.resume_vectors is not None else resume_vector
                self.resume_ids.append(resume_id)
            
            # 更新时间戳
            self.resume_last_updated[resume_id] = datetime.now()
            
            # 从待更新列表中移除
            if resume_id in self.pending_resume_updates:
                self.pending_resume_updates.remove(resume_id)
                
            logger.info(f"已更新简历 {resume_id} 的向量表示")
            return True
        except Exception as e:
            logger.error(f"更新简历向量时出错: {str(e)}", exc_info=True)
            # 添加到待更新列表
            self.pending_resume_updates.add(resume_id)
            return False
    
    async def schedule_job_update(self, job_id: int) -> bool:
        """安排职位向量更新（加入待更新队列）"""
        if not self.initialized:
            logger.warning(f"向量搜索服务未初始化，职位 {job_id} 将在初始化时更新")
            return False
            
        self.pending_job_updates.add(job_id)
        logger.debug(f"职位 {job_id} 已加入待更新队列，当前队列长度: {len(self.pending_job_updates)}")
        
        # 检查是否需要触发批量更新
        if len(self.pending_job_updates) >= self.max_pending_updates and not self.update_in_progress:
            logger.info(f"待更新职位数量达到阈值 {self.max_pending_updates}，将触发批量更新")
            return True
            
        return False
    
    async def schedule_resume_update(self, resume_id: int) -> bool:
        """安排简历向量更新（加入待更新队列）"""
        if not self.initialized:
            logger.warning(f"向量搜索服务未初始化，简历 {resume_id} 将在初始化时更新")
            return False
            
        self.pending_resume_updates.add(resume_id)
        logger.debug(f"简历 {resume_id} 已加入待更新队列，当前队列长度: {len(self.pending_resume_updates)}")
        
        # 检查是否需要触发批量更新
        if len(self.pending_resume_updates) >= self.max_pending_updates and not self.update_in_progress:
            logger.info(f"待更新简历数量达到阈值 {self.max_pending_updates}，将触发批量更新")
            return True
            
        return False
    
    async def batch_update(self, db: Session) -> bool:
        """批量更新向量索引"""
        if self.update_in_progress:
            logger.warning("批量更新已在进行中，跳过本次更新请求")
            return False
            
        try:
            self.update_in_progress = True
            start_time = time.time()
            
            # 复制待更新列表，避免在更新过程中被修改
            job_updates = list(self.pending_job_updates)
            resume_updates = list(self.pending_resume_updates)
            
            update_count = 0
            
            # 批量更新职位
            for job_id in job_updates:
                success = await self.update_job_vector(db, job_id)
                if success:
                    update_count += 1
            
            # 批量更新简历
            for resume_id in resume_updates:
                success = await self.update_resume_vector(db, resume_id)
                if success:
                    update_count += 1
            
            # 检查是否有剩余未更新的项
            remaining_updates = len(self.pending_job_updates) + len(self.pending_resume_updates)
            
            processing_time = time.time() - start_time
            logger.info(f"批量更新完成，共更新 {update_count} 个项目，耗时: {processing_time:.3f}秒，剩余 {remaining_updates} 个待更新项")
            return True
        except Exception as e:
            logger.error(f"批量更新向量索引时出错: {str(e)}", exc_info=True)
            return False
        finally:
            self.update_in_progress = False
    
    async def remove_job_vector(self, job_id: int) -> bool:
        """从索引中移除职位向量"""
        try:
            if not self.initialized or job_id not in self.job_ids:
                logger.warning(f"职位 {job_id} 不在向量索引中，无需移除")
                return True
                
            idx = self.job_ids.index(job_id)
            
            # 移除对应的向量和ID
            self.job_ids.pop(idx)
            if self.job_vectors is not None and self.job_vectors.shape[0] > idx:
                # 删除矩阵中的行
                mask = np.ones(self.job_vectors.shape[0], dtype=bool)
                mask[idx] = False
                self.job_vectors = self.job_vectors[mask]
            
            # 移除更新时间记录
            if job_id in self.job_last_updated:
                del self.job_last_updated[job_id]
                
            # 从待更新列表中移除
            if job_id in self.pending_job_updates:
                self.pending_job_updates.remove(job_id)
                
            logger.info(f"已从向量索引中移除职位 {job_id}")
            return True
        except Exception as e:
            logger.error(f"从索引中移除职位 {job_id} 时出错: {str(e)}", exc_info=True)
            return False
    
    async def remove_resume_vector(self, resume_id: int) -> bool:
        """从索引中移除简历向量"""
        try:
            if not self.initialized or resume_id not in self.resume_ids:
                logger.warning(f"简历 {resume_id} 不在向量索引中，无需移除")
                return True
                
            idx = self.resume_ids.index(resume_id)
            
            # 移除对应的向量和ID
            self.resume_ids.pop(idx)
            if self.resume_vectors is not None and self.resume_vectors.shape[0] > idx:
                # 删除矩阵中的行
                mask = np.ones(self.resume_vectors.shape[0], dtype=bool)
                mask[idx] = False
                self.resume_vectors = self.resume_vectors[mask]
            
            # 移除更新时间记录
            if resume_id in self.resume_last_updated:
                del self.resume_last_updated[resume_id]
                
            # 从待更新列表中移除
            if resume_id in self.pending_resume_updates:
                self.pending_resume_updates.remove(resume_id)
                
            logger.info(f"已从向量索引中移除简历 {resume_id}")
            return True
        except Exception as e:
            logger.error(f"从索引中移除简历 {resume_id} 时出错: {str(e)}", exc_info=True)
            return False
    
    async def get_vector_job_recommendations(
        self, 
        db: Session, 
        resume_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """基于向量搜索为简历推荐职位"""
        try:
            if not self.initialized:
                logger.warning(f"向量搜索服务未初始化，尝试为简历 {resume_id} 初始化")
                await self.initialize(db)
                if not self.initialized:
                    logger.error(f"向量搜索服务初始化失败，无法为简历 {resume_id} 提供推荐")
                    return []
            
            # 获取简历
            if resume_id not in self.resume_ids:
                logger.warning(f"简历 {resume_id} 不在向量索引中，尝试更新")
                resume = db.query(Resume).filter(Resume.id == resume_id).first()
                if not resume:
                    logger.error(f"数据库中找不到简历 {resume_id}")
                    return []
                
                # 如果是新简历，添加到索引
                success = await self.update_resume_vector(db, resume_id)
                if not success or resume_id not in self.resume_ids:
                    logger.error(f"无法将简历 {resume_id} 添加到向量索引")
                    return []
                logger.info(f"已将简历 {resume_id} 添加到向量索引")
            
            # 获取简历向量
            resume_idx = self.resume_ids.index(resume_id)
            resume_vector = self.resume_vectors[resume_idx]
            
            # 计算与所有职位的相似度
            try:
                similarities = cosine_similarity(resume_vector, self.job_vectors).flatten()
            except Exception as e:
                logger.error(f"计算简历 {resume_id} 与职位的相似度时出错: {str(e)}")
                return []
            
            # 获取前N个最相似的职位
            try:
                top_indices = np.argsort(similarities)[::-1][:limit]
            except Exception as e:
                logger.error(f"排序简历 {resume_id} 的相似度结果时出错: {str(e)}")
                return []
            
            # 构建结果
            recommendations = []
            for idx in top_indices:
                try:
                    similarity_score = float(similarities[idx])
                    if similarity_score <= 0:
                        continue
                    
                    job_id = self.job_ids[idx]
                    job = db.query(Job).filter(Job.id == job_id).first()
                    if not job:
                        logger.warning(f"找不到职位 {job_id}，该职位可能已被删除")
                        continue
                    
                    # 获取简历和职位的原始文本，用于提取技能匹配
                    resume = db.query(Resume).filter(Resume.id == resume_id).first()
                    if not resume:
                        logger.warning(f"找不到简历 {resume_id}，跳过技能匹配计算")
                        continue
                        
                    resume_text = f"{resume.title} {resume.summary or ''} {resume.skills or ''}"
                    job_text = f"{job.title} {job.description} {job.requirements or ''}"
                    
                    # 计算技能匹配分数
                    skill_score, matched_skills = self._get_skill_match_score(job_text, resume_text)
                    
                    # 计算最终分数，结合相似度和技能匹配
                    final_score = 0.7 * similarity_score + 0.3 * skill_score
                    
                    recommendations.append({
                        "id": job_id,
                        "title": job.title,
                        "company": job.company,
                        "match_score": final_score,
                        "similarity": similarity_score,
                        "skill_score": skill_score,
                        "matched_skills": matched_skills
                    })
                except Exception as e:
                    logger.error(f"处理职位推荐结果时出错 (简历: {resume_id}, 索引: {idx}): {str(e)}")
                    continue
            
            # 按最终分数重新排序
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            
            logger.info(f"成功为简历 {resume_id} 找到 {len(recommendations)} 个匹配职位")
            return recommendations
        except Exception as e:
            logger.error(f"获取职位推荐时出错: {str(e)}", exc_info=True)
            return []
    
    async def get_vector_resume_recommendations(
        self, 
        db: Session, 
        job_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """基于向量搜索为职位推荐简历"""
        try:
            if not self.initialized:
                await self.initialize(db)
                if not self.initialized:
                    return []
            
            # 获取职位
            if job_id not in self.job_ids:
                logger.warning(f"职位 {job_id} 不在向量索引中")
                job = db.query(Job).filter(Job.id == job_id).first()
                if not job:
                    return []
                
                # 如果是新职位，添加到索引
                await self.update_job_vector(db, job_id)
                if job_id not in self.job_ids:
                    return []
            
            # 获取职位向量
            job_idx = self.job_ids.index(job_id)
            job_vector = self.job_vectors[job_idx]
            
            # 计算与所有简历的相似度
            similarities = cosine_similarity(job_vector, self.resume_vectors).flatten()
            
            # 获取前N个最相似的简历
            top_indices = np.argsort(similarities)[::-1][:limit]
            
            # 构建结果
            recommendations = []
            for idx in top_indices:
                similarity_score = float(similarities[idx])
                if similarity_score <= 0:
                    continue
                
                resume_id = self.resume_ids[idx]
                resume = db.query(Resume).filter(Resume.id == resume_id).first()
                if not resume:
                    continue
                
                # 获取用户信息
                user = db.query(User).filter(User.id == resume.user_id).first() if resume.user_id else None
                
                # 获取简历和职位的原始文本，用于提取技能匹配
                job = db.query(Job).filter(Job.id == job_id).first()
                job_text = f"{job.title} {job.description} {job.requirements or ''}"
                resume_text = f"{resume.title} {resume.summary or ''} {resume.skills or ''}"
                
                # 计算技能匹配分数
                skill_score, matched_skills = self._get_skill_match_score(job_text, resume_text)
                
                # 计算最终分数，结合相似度和技能匹配
                final_score = 0.7 * similarity_score + 0.3 * skill_score
                
                user_info = {
                    "id": user.id if user else None,
                    "name": user.name if user else "Unknown",
                    "email": user.email if user else None
                } if user else {}
                
                recommendations.append({
                    "id": resume_id,
                    "title": resume.title,
                    "user": user_info,
                    "match_score": final_score,
                    "similarity": similarity_score,
                    "skill_score": skill_score,
                    "matched_skills": matched_skills
                })
            
            # 按最终分数重新排序
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            
            return recommendations
        except Exception as e:
            logger.error(f"获取简历推荐时出错: {str(e)}")
            return []


# 创建服务实例
vector_search_service = VectorSearchService() 