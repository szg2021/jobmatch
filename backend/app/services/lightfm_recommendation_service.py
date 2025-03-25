import os
import pickle
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

# 导入LightFM库和相关组件
from lightfm import LightFM
from lightfm.data import Dataset
from scipy.sparse import csr_matrix, vstack
from sklearn.feature_extraction.text import TfidfVectorizer

# 导入数据库模型（这些导入将根据实际项目结构调整）
from app.models.job import Job
from app.models.resume import Resume
from app.models.application import Application
from app.models.user import User

# 设置日志
logger = logging.getLogger(__name__)

# 常量定义
MODEL_DIR = Path("./data/models")
MODEL_PATH = MODEL_DIR / "lightfm_model.pkl"
DATASET_PATH = MODEL_DIR / "lightfm_dataset.pkl"
VECTORIZERS_PATH = MODEL_DIR / "lightfm_vectorizers.pkl"

# 确保模型目录存在
MODEL_DIR.mkdir(parents=True, exist_ok=True)

class LightFMRecommender:
    """LightFM混合推荐系统实现"""
    
    def __init__(self):
        self.model = None
        self.dataset = None
        self.job_vectorizer = None
        self.resume_vectorizer = None
        self.job_features = None
        self.resume_features = None
        self.job_ids = []
        self.resume_ids = []
        self.load_model()
    
    def load_model(self) -> bool:
        """从磁盘加载模型和辅助数据"""
        try:
            if MODEL_PATH.exists() and DATASET_PATH.exists() and VECTORIZERS_PATH.exists():
                logger.info("找到现有的LightFM模型文件，尝试加载")
                try:
                    with open(MODEL_PATH, 'rb') as f:
                        self.model = pickle.load(f)
                    
                    with open(DATASET_PATH, 'rb') as f:
                        data = pickle.load(f)
                        self.dataset = data['dataset']
                        self.job_ids = data['job_ids']
                        self.resume_ids = data['resume_ids']
                        
                    with open(VECTORIZERS_PATH, 'rb') as f:
                        vectorizers = pickle.load(f)
                        self.job_vectorizer = vectorizers['job_vectorizer']
                        self.resume_vectorizer = vectorizers['resume_vectorizer']
                        self.job_features = vectorizers.get('job_features')
                        self.resume_features = vectorizers.get('resume_features')
                    
                    # 验证模型的完整性
                    if not self.model or not self.dataset or not self.job_vectorizer or not self.resume_vectorizer:
                        logger.warning("LightFM模型已加载但部分组件缺失，可能需要重新训练")
                        return False
                        
                    logger.info(f"成功加载LightFM模型和相关数据，包含 {len(self.job_ids)} 个职位和 {len(self.resume_ids)} 个简历")
                    return True
                except (pickle.UnpicklingError, EOFError, AttributeError) as e:
                    logger.error(f"加载LightFM模型时文件损坏或格式不兼容: {str(e)}")
                    # 尝试删除损坏的文件
                    try:
                        if MODEL_PATH.exists():
                            MODEL_PATH.unlink()
                        if DATASET_PATH.exists():
                            DATASET_PATH.unlink()
                        if VECTORIZERS_PATH.exists():
                            VECTORIZERS_PATH.unlink()
                        logger.info("已删除损坏的模型文件，下次启动时将重新训练")
                    except Exception as del_err:
                        logger.error(f"删除损坏的模型文件时出错: {str(del_err)}")
                    return False
            else:
                missing_files = []
                if not MODEL_PATH.exists():
                    missing_files.append("模型文件")
                if not DATASET_PATH.exists():
                    missing_files.append("数据集文件")
                if not VECTORIZERS_PATH.exists():
                    missing_files.append("向量化器文件")
                    
                logger.warning(f"找不到完整的LightFM模型文件(缺少: {', '.join(missing_files)})，需要重新训练")
                return False
        except Exception as e:
            logger.error(f"加载LightFM模型时出错: {str(e)}", exc_info=True)
            return False
    
    def save_model(self):
        """保存模型和辅助数据到磁盘"""
        try:
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(self.model, f)
            
            data = {
                'dataset': self.dataset,
                'job_ids': self.job_ids,
                'resume_ids': self.resume_ids,
            }
            with open(DATASET_PATH, 'wb') as f:
                pickle.dump(data, f)
            
            vectorizers = {
                'job_vectorizer': self.job_vectorizer,
                'resume_vectorizer': self.resume_vectorizer,
                'job_features': self.job_features,
                'resume_features': self.resume_features,
            }
            with open(VECTORIZERS_PATH, 'wb') as f:
                pickle.dump(vectorizers, f)
                
            logger.info("LightFM模型和相关数据已成功保存")
            return True
        except Exception as e:
            logger.error(f"保存LightFM模型时出错: {str(e)}")
            return False
    
    def prepare_data(self, db: Session) -> bool:
        """准备训练所需的数据"""
        try:
            # 初始化数据集
            self.dataset = Dataset()
            
            # 获取所有简历和职位
            resumes = db.query(Resume).all()
            jobs = db.query(Job).all()
            
            # 存储ID列表以便后续推荐时使用
            self.resume_ids = [resume.id for resume in resumes]
            self.job_ids = [job.id for job in jobs]
            
            # 将用户和项目(职位)添加到数据集
            self.dataset.fit(users=self.resume_ids, items=self.job_ids)
            
            # 构建互动数据 - 从申请记录中获取
            applications = db.query(Application).all()
            interactions = []
            for app in applications:
                if app.resume_id in self.resume_ids and app.job_id in self.job_ids:
                    interactions.append((app.resume_id, app.job_id, 1.0))
            
            # 创建交互矩阵
            (interactions_matrix, weights) = self.dataset.build_interactions(interactions)
            
            # 处理文本特征 - 为职位和简历创建TF-IDF向量
            self.job_vectorizer = TfidfVectorizer(max_features=1000)
            self.resume_vectorizer = TfidfVectorizer(max_features=1000)
            
            # 提取简历和职位的文本
            job_texts = [f"{job.title} {job.description}" for job in jobs]
            resume_texts = [f"{resume.title} {resume.summary} {resume.skills}" for resume in resumes]
            
            # 转换文本为特征矩阵
            if job_texts:
                job_features_matrix = self.job_vectorizer.fit_transform(job_texts)
                self.job_features = csr_matrix(job_features_matrix)
            else:
                self.job_features = csr_matrix((0, 0))
            
            if resume_texts:
                resume_features_matrix = self.resume_vectorizer.fit_transform(resume_texts)
                self.resume_features = csr_matrix(resume_features_matrix)
            else:
                self.resume_features = csr_matrix((0, 0))
            
            # 转换为LightFM格式
            job_features_dict = {job_id: [f"job_{i}" for i in range(1000)] for job_id in self.job_ids}
            resume_features_dict = {resume_id: [f"resume_{i}" for i in range(1000)] for resume_id in self.resume_ids}
            
            # 将特征添加到数据集
            self.dataset.fit_partial(
                items_features=job_features_dict,
                users_features=resume_features_dict
            )
            
            # 构建特征矩阵
            item_features = self.dataset.build_item_features(
                ((item_id, [f"job_{i}" for i in range(1000)]) for item_id in self.job_ids)
            )
            user_features = self.dataset.build_user_features(
                ((user_id, [f"resume_{i}" for i in range(1000)]) for user_id in self.resume_ids)
            )
            
            logger.info(f"数据准备完成，{len(self.resume_ids)}个简历，{len(self.job_ids)}个职位，{len(interactions)}个交互")
            
            # 保存处理好的数据
            self.save_model()
            
            return interactions_matrix, weights, item_features, user_features
        except Exception as e:
            logger.error(f"准备训练数据时出错: {str(e)}")
            return None
    
    def train_model(self, db: Session = None, epochs: int = None, config: Dict[str, Any] = None):
        """训练LightFM模型"""
        try:
            # 获取配置参数，使用延迟导入避免循环依赖
            if config is None:
                # 在函数内部导入，避免循环依赖
                def get_config_for_training(db_session: Session) -> Dict[str, Any]:
                    from app.crud.crud_recommendation_config import recommendation_config
                    return recommendation_config.get_config_for_training(db_session)
                
                config = get_config_for_training(db)
            
            # 确保epochs是整数
            if epochs is not None:
                epochs = int(epochs)
            elif config and "epochs" in config:
                epochs = int(config.get("epochs", 30))
            else:
                epochs = 30
            
            # 设置其他训练参数
            learning_rate = float(config.get("learning_rate", 0.05))
            loss_function = config.get("loss_function", "warp")
            embedding_dim = int(config.get("embedding_dim", 64))
            user_alpha = float(config.get("user_alpha", 1e-6))
            item_alpha = float(config.get("item_alpha", 1e-6))
            num_threads = int(config.get("num_threads", 4))
            
            # 准备数据
            data = self.prepare_data(db)
            if data is None:
                logger.error("无法准备训练数据，训练已取消")
                return False
                
            interactions_matrix, weights, item_features, user_features = data
            
            # 初始化模型
            self.model = LightFM(
                loss=loss_function,
                learning_rate=learning_rate,
                no_components=embedding_dim,
                user_alpha=user_alpha,
                item_alpha=item_alpha
            )
            
            # 训练模型
            logger.info(f"开始训练LightFM模型，epochs={epochs}，loss={loss_function}")
            start_time = datetime.now()
            
            self.model.fit(
                interactions=interactions_matrix,
                sample_weight=weights,
                user_features=user_features,
                item_features=item_features,
                epochs=epochs,
                num_threads=num_threads,
                verbose=True
            )
            
            end_time = datetime.now()
            training_time = (end_time - start_time).total_seconds()
            logger.info(f"LightFM模型训练完成，用时{training_time}秒")
            
            # 保存模型
            self.save_model()
            return True
        except Exception as e:
            logger.error(f"训练LightFM模型时出错: {str(e)}")
            return False
    
    def recommend_jobs_for_resume(self, resume_id: int, n: int = 10) -> List[Tuple[int, float]]:
        """为简历推荐职位"""
        try:
            if self.model is None or resume_id not in self.resume_ids:
                return []
            
            # 获取用户内部ID
            user_idx = self.resume_ids.index(resume_id)
            
            # 生成推荐
            scores = self.model.predict(
                user_ids=[user_idx],
                item_ids=list(range(len(self.job_ids))),
                user_features=None,  # 暂不使用用户特征
                item_features=None   # 暂不使用项目特征
            )
            
            # 创建(job_id, score)对并排序
            job_scores = [(self.job_ids[i], float(scores[i])) for i in range(len(self.job_ids))]
            job_scores.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前n个结果
            return job_scores[:n]
        except Exception as e:
            logger.error(f"为简历{resume_id}生成职位推荐时出错: {str(e)}")
            return []
    
    def recommend_resumes_for_job(self, job_id: int, n: int = 10) -> List[Tuple[int, float]]:
        """为职位推荐简历"""
        try:
            if self.model is None or job_id not in self.job_ids:
                return []
            
            # 获取项目内部ID
            item_idx = self.job_ids.index(job_id)
            
            # 生成推荐
            scores = self.model.predict(
                user_ids=list(range(len(self.resume_ids))),
                item_ids=[item_idx],
                user_features=None,  # 暂不使用用户特征
                item_features=None   # 暂不使用项目特征
            )
            
            # 创建(resume_id, score)对并排序
            resume_scores = [(self.resume_ids[i], float(scores[i])) for i in range(len(self.resume_ids))]
            resume_scores.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前n个结果
            return resume_scores[:n]
        except Exception as e:
            logger.error(f"为职位{job_id}生成简历推荐时出错: {str(e)}")
            return []

# 创建单例实例
lightfm_recommender = LightFMRecommender()

# 公共函数，供其他模块调用
async def prepare_and_train_lightfm(db: Session, config: Dict[str, Any] = None) -> bool:
    """准备并训练LightFM模型的异步函数"""
    try:
        return lightfm_recommender.train_model(db, config=config)
    except Exception as e:
        logger.error(f"准备并训练LightFM模型时出错: {str(e)}")
        return False

async def get_lightfm_job_recommendations(
    resume_id: int, 
    db: Session, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """根据简历获取职位推荐"""
    try:
        if not is_lightfm_ready():
            logger.warning("LightFM模型未就绪，无法提供推荐")
            return []
            
        # 确保resume_id是整数
        try:
            resume_id = int(resume_id)
        except (ValueError, TypeError):
            logger.error(f"无效的简历ID: {resume_id}, 类型: {type(resume_id)}")
            return []
        
        # 检查resume_id是否在模型的用户列表中
        if resume_id not in lightfm_recommender.resume_ids:
            logger.warning(f"简历ID {resume_id} 不在LightFM模型中，需要重新训练模型以包含此简历")
            return []
            
        # 获取推荐
        try:
            recommendations = lightfm_recommender.recommend_jobs_for_resume(resume_id, n=limit)
        except Exception as rec_error:
            logger.error(f"调用LightFM推荐时出错: {str(rec_error)}", exc_info=True)
            return []
        
        if not recommendations:
            logger.warning(f"LightFM没有为简历 {resume_id} 找到任何推荐")
            return []
            
        # 构建结果
        result = []
        for job_id, score in recommendations:
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    result.append({
                        "id": job_id,
                        "title": job.title,
                        "company": job.company,
                        "match_score": float(score),  # 确保score是Python浮点数
                        "algorithm": "lightfm"
                    })
                else:
                    logger.warning(f"推荐的职位ID {job_id} 在数据库中不存在")
            except Exception as job_error:
                logger.error(f"处理推荐的职位ID {job_id} 时出错: {str(job_error)}")
                continue
        
        logger.info(f"LightFM为简历 {resume_id} 生成了 {len(result)} 个推荐结果")
        return result
    except Exception as e:
        logger.error(f"获取简历{resume_id}的LightFM职位推荐时出错: {str(e)}", exc_info=True)
        return []

async def get_lightfm_resume_recommendations(
    job_id: int, 
    db: Session, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """根据职位获取简历推荐"""
    try:
        recommendations = lightfm_recommender.recommend_resumes_for_job(job_id, n=limit)
        
        result = []
        for resume_id, score in recommendations:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            user = db.query(User).filter(User.id == resume.user_id).first() if resume else None
            
            if resume and user:
                result.append({
                    "id": resume_id,
                    "title": resume.title,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    },
                    "match_score": score,
                    "algorithm": "lightfm"
                })
        
        return result
    except Exception as e:
        logger.error(f"获取职位{job_id}的LightFM简历推荐时出错: {str(e)}")
        return []

def is_lightfm_ready() -> bool:
    """检查LightFM模型是否已训练并准备好使用"""
    return lightfm_recommender.model is not None 