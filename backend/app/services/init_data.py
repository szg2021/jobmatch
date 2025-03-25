import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
from pathlib import Path

from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.document import Document, DocumentType, Job, Resume, ProcessStatus

# 获取日志记录器
logger = logging.getLogger("app.services.init_data")

async def init_test_users(db: Session):
    """
    初始化测试用户数据
    """
    logger.info("初始化测试用户数据...")
    
    # 检查是否已有用户，避免重复创建
    existing_user_count = db.query(User).count()
    if existing_user_count > 0:
        logger.info(f"已存在 {existing_user_count} 个用户，跳过初始化")
        return
    
    # 创建管理员用户
    admin_user = User(
        email="admin@example.com",
        phone="13900000000",
        hashed_password=get_password_hash("admin123"),
        full_name="系统管理员",
        role=UserRole.ADMIN,
        is_active=True
    )
    
    # 创建企业用户
    company_user = User(
        email="company@example.com",
        phone="13800000001",
        hashed_password=get_password_hash("123456"),
        full_name="示例企业",
        role=UserRole.COMPANY,
        is_active=True,
        company_name="示例科技有限公司",
        company_size="100-499人",
        company_industry="互联网/IT/科技"
    )
    
    # 创建求职者用户
    jobseeker_user = User(
        email="user@example.com",
        phone="13700000002",
        hashed_password=get_password_hash("123456"),
        full_name="张三",
        role=UserRole.JOBSEEKER,
        is_active=True
    )
    
    # 添加到数据库
    db.add(admin_user)
    db.add(company_user)
    db.add(jobseeker_user)
    db.commit()
    
    logger.info("测试用户初始化完成")
    return [admin_user, company_user, jobseeker_user]

async def init_test_documents(db: Session, users):
    """
    初始化测试文档、职位和简历数据
    """
    logger.info("初始化测试文档数据...")
    
    # 检查是否已有文档，避免重复创建
    existing_doc_count = db.query(Document).count()
    if existing_doc_count > 0:
        logger.info(f"已存在 {existing_doc_count} 个文档，跳过初始化")
        return
    
    # 获取企业和求职者用户
    company_user = None
    jobseeker_user = None
    
    for user in users:
        if user.role == UserRole.COMPANY:
            company_user = user
        elif user.role == UserRole.JOBSEEKER:
            jobseeker_user = user
    
    if not company_user or not jobseeker_user:
        logger.error("找不到企业或求职者用户，无法创建测试文档")
        return
    
    # 创建上传目录
    uploads_dir = Path("./uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # 创建职位文档
    job_doc = Document(
        filename="测试职位.txt",
        file_path="./uploads/test_job.txt",
        content_type="text/plain",
        file_size=1024,
        user_id=company_user.id,
        document_type=DocumentType.JOB,
        process_status=ProcessStatus.COMPLETED,
        original_text="这是一个Python后端开发工程师职位，要求3年以上经验，熟悉FastAPI、SQLAlchemy等技术。",
        vector_id="job-test-1"
    )
    db.add(job_doc)
    db.flush()
    
    # 创建职位
    job = Job(
        document_id=job_doc.id,
        user_id=company_user.id,
        title="Python后端开发工程师",
        company_name=company_user.company_name,
        location="北京",
        job_type="全职",
        salary_range="25k-35k",
        requirements="Python,FastAPI,SQLAlchemy,Redis",
        content="我们正在寻找一位经验丰富的Python后端开发工程师。\n\n职责:\n- 开发和维护后端API系统\n- 与前端团队协作实现产品需求\n\n要求:\n- 3年以上Python开发经验\n- 熟悉FastAPI或Flask框架\n- 熟悉SQL和NoSQL数据库\n- 良好的沟通和团队协作能力",
        is_active=True,
        created_at=datetime.now()
    )
    db.add(job)
    
    # 创建简历文档
    resume_doc = Document(
        filename="张三的简历.pdf",
        file_path="./uploads/test_resume.pdf",
        content_type="application/pdf",
        file_size=2048,
        user_id=jobseeker_user.id,
        document_type=DocumentType.RESUME,
        process_status=ProcessStatus.COMPLETED,
        original_text="姓名：张三\n学历：本科，计算机科学\n工作经验：3年\n技能：Python, JavaScript, SQL, React\n项目经验：...",
        vector_id="resume-test-1"
    )
    db.add(resume_doc)
    db.flush()
    
    # 创建简历
    resume = Resume(
        document_id=resume_doc.id,
        user_id=jobseeker_user.id,
        name=jobseeker_user.full_name,
        skills="Python,JavaScript,SQL,React",
        education="本科，计算机科学",
        experience="3年",
        content="个人简介：\n拥有3年全栈开发经验，熟悉Python后端和React前端开发。\n\n工作经历：\n2020-2023 某科技公司 全栈开发工程师",
        created_at=datetime.now()
    )
    db.add(resume)
    
    # 创建测试文件
    with open(job_doc.file_path, "w") as f:
        f.write(job_doc.original_text)
    
    # 模拟简历PDF文件（实际上是文本文件）
    with open(resume_doc.file_path, "w") as f:
        f.write(resume_doc.original_text)
    
    db.commit()
    logger.info("测试文档初始化完成")

async def init_data(db: Session):
    """
    初始化所有测试数据
    """
    try:
        users = await init_test_users(db)
        if users:
            await init_test_documents(db, users)
        return True
    except Exception as e:
        logger.error(f"初始化测试数据失败: {str(e)}")
        return False 