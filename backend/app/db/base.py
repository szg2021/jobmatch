# 数据库基类，包含所有模型的导入
from app.db.session import Base

# 导入所有模型，以便在Base.metadata.create_all()时创建所有表
from app.models.user import User
from app.models.document import Document, Job, Resume 