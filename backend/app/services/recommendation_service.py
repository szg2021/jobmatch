from typing import List, Dict, Any, Optional
import os
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Resume, Job
from app.models.user import User

# 获取日志记录器
logger = logging.getLogger("app.services.recommendation")

# 检查是否处于开发环境
DEV_MODE = os.environ.get("APP_ENV", "development") == "development" or settings.USE_SQLITE

# 尝试导入Weaviate客户端，如果在开发环境则使用模拟实现
weaviate_client = None

if not DEV_MODE:
    try:
        import weaviate
        # 连接到Weaviate
        auth_config = None
        if settings.WEAVIATE_API_KEY:
            auth_config = weaviate.AuthApiKey(api_key=settings.WEAVIATE_API_KEY)
            
        weaviate_client = weaviate.Client(
            url=settings.WEAVIATE_URL,
            auth_client_secret=auth_config
        )
        logger.info(f"Weaviate 连接成功: {settings.WEAVIATE_URL}")
    except Exception as e:
        logger.error(f"Weaviate 连接失败: {str(e)}")
        weaviate_client = None
else:
    logger.info("开发模式：使用模拟的Weaviate客户端")


class WeaviateClient:
    """Weaviate向量数据库客户端"""
    
    def __init__(self):
        """初始化Weaviate客户端"""
        self.client = None
        try:
            auth_config = weaviate.auth.AuthApiKey(api_key=settings.WEAVIATE_API_KEY) if settings.WEAVIATE_API_KEY else None
            self.client = weaviate.Client(
                url=settings.WEAVIATE_URL,
                auth_client_secret=auth_config
            )
            
            # 检查连接
            if not self.client.is_ready():
                raise Exception("Weaviate服务不可用")
                
            # 确保模式存在
            self._ensure_schema_exists()
            
        except Exception as e:
            logger.error(f"初始化Weaviate客户端失败: {str(e)}")
            self.client = None
    
    def is_ready(self):
        """检查客户端是否准备就绪"""
        return self.client is not None
    
    def check_connection(self):
        """检查连接状态并尝试重新连接"""
        if self.client is None:
            try:
                auth_config = weaviate.auth.AuthApiKey(api_key=settings.WEAVIATE_API_KEY) if settings.WEAVIATE_API_KEY else None
                self.client = weaviate.Client(
                    url=settings.WEAVIATE_URL,
                    auth_client_secret=auth_config
                )
                
                if not self.client.is_ready():
                    raise Exception("Weaviate服务不可用")
                    
                # 确保模式存在
                self._ensure_schema_exists()
                return True
            except Exception as e:
                logger.error(f"重新连接Weaviate失败: {str(e)}")
                self.client = None
                return False
        return self.client.is_ready()
    
    def _ensure_schema_exists(self):
        """确保所需的模式存在"""
        if not self.client:
            raise Exception("Weaviate客户端未初始化")
            
        # 检查并创建Resume类
        if not self.client.schema.exists("Resume"):
            resume_class = {
                "class": "Resume",
                "description": "求职者简历",
                "vectorizer": "text2vec-openai",  # 使用OpenAI的文本向量化
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": settings.EMBEDDING_MODEL,
                        "modelVersion": "latest",
                        "type": "text"
                    }
                },
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "简历内容"
                    },
                    {
                        "name": "resumeId",
                        "dataType": ["int"],
                        "description": "简历ID"
                    },
                    {
                        "name": "userId",
                        "dataType": ["int"],
                        "description": "用户ID"
                    },
                    {
                        "name": "skills",
                        "dataType": ["text[]"],
                        "description": "技能列表"
                    }
                ]
            }
            self.client.schema.create_class(resume_class)
        
        # 检查并创建Job类
        if not self.client.schema.exists("Job"):
            job_class = {
                "class": "Job",
                "description": "工作岗位",
                "vectorizer": "text2vec-openai",  # 使用OpenAI的文本向量化
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": settings.EMBEDDING_MODEL,
                        "modelVersion": "latest",
                        "type": "text"
                    }
                },
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "岗位内容"
                    },
                    {
                        "name": "jobId",
                        "dataType": ["int"],
                        "description": "岗位ID"
                    },
                    {
                        "name": "userId",
                        "dataType": ["int"],
                        "description": "发布者ID"
                    },
                    {
                        "name": "isActive",
                        "dataType": ["boolean"],
                        "description": "是否活跃"
                    },
                    {
                        "name": "requirements",
                        "dataType": ["text[]"],
                        "description": "岗位要求"
                    }
                ]
            }
            self.client.schema.create_class(job_class)
    
    def add_resume(self, resume_id: int, user_id: int, content: str, skills: List[str] = None) -> str:
        """将简历添加到向量数据库"""
        if not self.client:
            if not self.check_connection():
                raise Exception("Weaviate客户端未初始化且无法重新连接")
        
        # 准备数据
        data = {
            "content": content,
            "resumeId": resume_id,
            "userId": user_id
        }
        
        if skills:
            data["skills"] = skills
        
        # 添加到Weaviate
        try:
            result = self.client.data_object.create(
                data_object=data,
                class_name="Resume"
            )
            return result  # 返回向量ID
        except Exception as e:
            logger.error(f"添加简历到Weaviate失败: {str(e)}")
            raise
    
    def add_job(self, job_id: int, user_id: int, content: str, is_active: bool = True, requirements: List[str] = None) -> str:
        """将工作岗位添加到向量数据库"""
        if not self.client:
            if not self.check_connection():
                raise Exception("Weaviate客户端未初始化且无法重新连接")
        
        # 准备数据
        data = {
            "content": content,
            "jobId": job_id,
            "userId": user_id,
            "isActive": is_active
        }
        
        if requirements:
            data["requirements"] = requirements
        
        # 添加到Weaviate
        try:
            result = self.client.data_object.create(
                data_object=data,
                class_name="Job"
            )
            return result  # 返回向量ID
        except Exception as e:
            logger.error(f"添加岗位到Weaviate失败: {str(e)}")
            raise
    
    def update_resume(self, vector_id: str, content: str = None, skills: List[str] = None) -> None:
        """更新简历向量"""
        if not self.client:
            if not self.check_connection():
                raise Exception("Weaviate客户端未初始化且无法重新连接")
        
        # 准备更新数据
        data = {}
        if content:
            data["content"] = content
        if skills:
            data["skills"] = skills
        
        if not data:
            return  # 没有要更新的内容
        
        # 更新Weaviate中的对象
        try:
            self.client.data_object.update(
                uuid=vector_id,
                data_object=data,
                class_name="Resume"
            )
        except Exception as e:
            logger.error(f"更新简历向量失败: {str(e)}")
            raise
    
    def update_job(self, vector_id: str, content: str = None, is_active: bool = None, requirements: List[str] = None) -> None:
        """更新岗位向量"""
        if not self.client:
            if not self.check_connection():
                raise Exception("Weaviate客户端未初始化且无法重新连接")
        
        # 准备更新数据
        data = {}
        if content:
            data["content"] = content
        if is_active is not None:
            data["isActive"] = is_active
        if requirements:
            data["requirements"] = requirements
        
        if not data:
            return  # 没有要更新的内容
        
        # 更新Weaviate中的对象
        try:
            self.client.data_object.update(
                uuid=vector_id,
                data_object=data,
                class_name="Job"
            )
        except Exception as e:
            logger.error(f"更新岗位向量失败: {str(e)}")
            raise
    
    def get_resume_recommendations(self, job_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """基于岗位获取简历推荐"""
        if not self.client:
            if not self.check_connection():
                logger.warning("Weaviate客户端未初始化且无法重新连接")
                return []
        
        try:
            # 首先获取岗位内容
            job_result = self.client.query.get(
                class_name="Job",
                properties=["content"],
                where={
                    "path": ["jobId"],
                    "operator": "Equal",
                    "valueNumber": job_id
                }
            ).do()
            
            if not job_result or not job_result["data"]["Get"]["Job"]:
                return []
            
            job_content = job_result["data"]["Get"]["Job"][0]["content"]
            
            # 基于岗位内容推荐简历
            result = (
                self.client.query
                .get("Resume", ["resumeId", "userId", "content", "skills"])
                .with_near_text({"concepts": [job_content]})
                .with_limit(limit)
                .do()
            )
            
            if not result or not result["data"]["Get"]["Resume"]:
                return []
            
            return result["data"]["Get"]["Resume"]
            
        except Exception as e:
            logger.error(f"获取简历推荐失败: {str(e)}")
            return []
    
    def get_job_recommendations(self, resume_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """基于简历获取岗位推荐"""
        if not self.client:
            if not self.check_connection():
                logger.warning("Weaviate客户端未初始化且无法重新连接")
                return []
        
        try:
            # 首先获取简历内容
            resume_result = self.client.query.get(
                class_name="Resume",
                properties=["content"],
                where={
                    "path": ["resumeId"],
                    "operator": "Equal",
                    "valueNumber": resume_id
                }
            ).do()
            
            if not resume_result or not resume_result["data"]["Get"]["Resume"]:
                return []
            
            resume_content = resume_result["data"]["Get"]["Resume"][0]["content"]
            
            # 基于简历内容推荐岗位
            result = (
                self.client.query
                .get("Job", ["jobId", "userId", "content", "requirements"])
                .with_near_text({"concepts": [resume_content]})
                .with_where({
                    "path": ["isActive"],
                    "operator": "Equal",
                    "valueBoolean": True
                })
                .with_limit(limit)
                .do()
            )
            
            if not result or not result["data"]["Get"]["Job"]:
                return []
            
            return result["data"]["Get"]["Job"]
            
        except Exception as e:
            logger.error(f"获取岗位推荐失败: {str(e)}")
            return []


# 创建全局Weaviate客户端实例
weaviate_client = WeaviateClient()


async def index_resume(db: Session, resume: Resume, document_text: str) -> str:
    """将简历索引到向量数据库"""
    # 从简历中提取技能（简化实现）
    skills = []
    if resume.skills:
        skills = [skill.strip() for skill in resume.skills.split(",")]
    
    # 添加到Weaviate
    vector_id = weaviate_client.add_resume(
        resume_id=resume.id,
        user_id=resume.user_id,
        content=document_text,
        skills=skills
    )
    
    return vector_id


async def index_job(db: Session, job: Job, document_text: str) -> str:
    """将岗位索引到向量数据库"""
    # 从岗位中提取要求（简化实现）
    requirements = []
    if job.requirements:
        # 简单分割处理，实际应用中可能需要更复杂的解析
        requirements = [req.strip() for req in job.requirements.split("\n") if req.strip()]
    
    # 添加到Weaviate
    vector_id = weaviate_client.add_job(
        job_id=job.id,
        user_id=job.user_id,
        content=document_text,
        is_active=job.is_active,
        requirements=requirements
    )
    
    return vector_id


async def update_resume_index(vector_id: str, resume: Resume, document_text: str) -> None:
    """更新简历索引"""
    # 从简历中提取技能（简化实现）
    skills = []
    if resume.skills:
        skills = [skill.strip() for skill in resume.skills.split(",")]
    
    # 更新Weaviate中的简历
    weaviate_client.update_resume(
        vector_id=vector_id,
        content=document_text,
        skills=skills
    )


async def update_job_index(vector_id: str, job: Job, document_text: str) -> None:
    """更新岗位索引"""
    # 从岗位中提取要求（简化实现）
    requirements = []
    if job.requirements:
        requirements = [req.strip() for req in job.requirements.split("\n") if req.strip()]
    
    # 更新Weaviate中的岗位
    weaviate_client.update_job(
        vector_id=vector_id,
        content=document_text,
        is_active=job.is_active,
        requirements=requirements
    )


async def get_recommended_resumes(db: Session, job_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    获取与指定职位匹配的简历推荐
    """
    # 获取职位信息
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        logger.error(f"职位不存在: {job_id}")
        return []
    
    if DEV_MODE:
        # 开发环境使用模拟数据
        logger.info(f"开发模式：生成与职位 {job_id} 匹配的模拟简历数据")
        
        # 获取所有简历以模拟推荐
        resumes = db.query(Resume).limit(limit).all()
        result = []
        
        for i, resume in enumerate(resumes):
            # 模拟匹配分数和细节
            match_score = min(100, 90 - i * 5)  # 递减的匹配分数
            
            # 构建推荐结果
            result.append({
                "resume_id": resume.id,
                "match_score": match_score,
                "match_details": {
                    "skills_match": min(100, match_score + 5),
                    "experience_match": min(100, match_score - 5),
                    "education_match": min(100, match_score + 10)
                },
                "resume": {
                    "id": resume.id,
                    "name": resume.name if hasattr(resume, 'name') else f"求职者-{resume.id}",
                    "skills": resume.skills if hasattr(resume, 'skills') and resume.skills else ["Python", "数据分析", "机器学习"],
                    "education": resume.education if hasattr(resume, 'education') else "本科",
                    "experience": resume.experience if hasattr(resume, 'experience') else "3年",
                }
            })
        
        return result
    
    # 生产环境使用Weaviate进行向量搜索
    if not weaviate_client:
        logger.error("Weaviate客户端未初始化")
        return []
    
    try:
        # 这里实现Weaviate搜索逻辑
        # ...
        pass
    except Exception as e:
        logger.error(f"获取简历推荐时发生错误: {str(e)}")
        return []


async def get_recommended_jobs(db: Session, resume_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    获取与指定简历匹配的职位推荐
    """
    # 获取简历信息
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        logger.error(f"简历不存在: {resume_id}")
        return []
    
    if DEV_MODE:
        # 开发环境使用模拟数据
        logger.info(f"开发模式：生成与简历 {resume_id} 匹配的模拟职位数据")
        
        # 获取所有职位以模拟推荐
        jobs = db.query(Job).filter(Job.is_active == True).limit(limit).all()
        result = []
        
        for i, job in enumerate(jobs):
            # 模拟匹配分数和细节
            match_score = min(100, 95 - i * 5)  # 递减的匹配分数
            
            # 构建推荐结果
            result.append({
                "job_id": job.id,
                "match_score": match_score,
                "match_details": {
                    "skills_match": min(100, match_score + 5),
                    "requirements_match": min(100, match_score - 10),
                    "location_match": min(100, match_score + 2)
                },
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "company_name": job.company_name,
                    "location": job.location,
                    "job_type": job.job_type,
                    "salary_range": job.salary_range,
                    "is_active": job.is_active,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                }
            })
        
        return result
    
    # 生产环境使用Weaviate进行向量搜索
    if not weaviate_client:
        logger.error("Weaviate客户端未初始化")
        return []
    
    try:
        # 这里实现Weaviate搜索逻辑
        # ...
        pass
    except Exception as e:
        logger.error(f"获取职位推荐时发生错误: {str(e)}")
        return [] 