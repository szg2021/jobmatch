# AI招聘推荐平台

基于AI技术的智能招聘推荐平台，通过向量化技术实现简历和职位的精准匹配。

## 项目特点

- 基于AI的匹配推荐，不依赖关键字搜索
- 使用向量数据库存储和检索简历和职位信息
- 整合多种开源技术：Weaviate、FastAPI、PyMuPDF等
- 外部API接入LLM和Embedding能力，支持多模型切换
- 强大的错误处理和系统健壮性设计
- 完善的日志记录系统与API速率限制保护
- 响应式前端设计，支持PC和移动设备
- 用户友好的界面与交互体验
- 高级筛选和搜索功能，支持多条件精准查询
- 统一的加载状态管理和组件风格

## 技术栈

- 前端：Vue3 + TypeScript + Element Plus + Vite + Pinia
- 后端：FastAPI + Python 3.10+
- 文档处理：PyMuPDF + Python-docx
- 数据库：PostgreSQL + Redis + Weaviate
- 推荐引擎：基于向量相似度的语义匹配

## 当前状态

系统已经完成的功能：

- ✅ 用户认证与权限管理系统
- ✅ 简历和职位文档上传、解析与向量化
- ✅ 基于向量相似度的推荐系统
- ✅ 完整的API端点实现
- ✅ 健壮性和容错机制
- ✅ 日志记录和系统监控
- ✅ API速率限制保护
- ✅ 前端全局错误处理和网络请求优化
- ✅ 前端用户认证功能（登录/注册）
- ✅ 前端简历上传与管理
- ✅ 前端职位推荐展示
- ✅ 前端职位管理功能（发布、编辑、删除）
- ✅ 响应式布局适配不同设备
- ✅ 高级搜索和筛选功能（职位市场、人才市场）
- ✅ 自动技能提取与技能建议功能
- ✅ 自定义匹配算法设置
- ✅ 个人中心完善（包括通知设置）
- ✅ 统一的UI组件和加载状态管理
- 🔄 推荐算法优化（进行中）
- 🔄 实时通知系统（计划中）
- 🔄 数据分析和可视化功能（计划中）

## 开发环境设置

### 系统要求

- Python 3.10+
- Node.js 18+ (前端开发)
- PostgreSQL 14+
- Redis 6+
- Weaviate 服务（可以使用Docker容器部署）

### 环境变量设置

在项目根目录创建`.env`文件，添加以下配置：

```
# PostgreSQL
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ai_recruitment
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Weaviate
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=

# OpenAI API (用于文本向量化)
OPENAI_API_KEY=your_openai_api_key
EMBEDDING_MODEL=text-embedding-ada-002
LLM_MODEL=gpt-3.5-turbo

# 文档存储路径
DOCUMENT_STORAGE_PATH=./uploads
MAX_DOCUMENT_SIZE=10
```

### 后端设置

1. 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 初始化数据库
```bash
cd backend
alembic upgrade head
```

4. 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload
```

5. 访问API文档
浏览器打开 http://localhost:8000/docs 可以查看和测试API

### 前端设置

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

3. 构建生产版本
```bash
npm run build
```

## 项目结构

```
ai-recruitment/
├── backend/                  # FastAPI后端
│   ├── app/                  # 应用代码
│   │   ├── api/              # API路由
│   │   │   └── endpoints/    # API端点实现
│   │   ├── core/             # 核心配置
│   │   ├── db/               # 数据库模型和连接
│   │   ├── models/           # 数据库模型
│   │   ├── schemas/          # Pydantic验证模型
│   │   ├── services/         # 业务逻辑服务
│   │   └── main.py           # 应用入口
│   ├── logs/                 # 日志文件
│   ├── tests/                # 测试代码
│   └── uploads/              # 上传文件存储
├── frontend/                 # Vue3前端
│   ├── public/               # 静态资源
│   ├── src/                  # 源代码
│   │   ├── assets/           # 资源文件
│   │   ├── components/       # 通用组件
│   │   │   ├── common/       # 常用UI组件
│   │   │   └── layout/       # 布局组件
│   │   ├── router/           # 路由配置
│   │   ├── store/            # Pinia状态管理
│   │   ├── utils/            # 工具函数
│   │   ├── views/            # 页面组件
│   │   │   ├── auth/         # 认证相关页面
│   │   │   └── dashboard/    # 主面板页面
│   │   └── main.ts           # 入口文件
│   └── tests/                # 测试代码
├── docker/                   # Docker配置
├── alembic/                  # 数据库迁移
├── requirements.txt          # 后端依赖列表
└── README.md                 # 项目说明
```

## 核心功能

### 用户管理

- 不同角色：管理员、求职者、企业用户
- 基于JWT的身份验证
- 细粒度的权限控制
- 用户个人资料管理
- 通知设置与偏好管理

### 文档处理

- 支持PDF和DOCX格式
- 智能提取文本内容
- 文档解析和结构化
- 技能和要求自动提取
- 技能建议与添加功能

### 推荐系统

- 基于Weaviate向量数据库的语义搜索
- 简历-职位双向推荐
- 自定义匹配评分算法
- 详细的匹配度分析
- 可调整匹配权重和算法类型

### 前端功能

- 响应式布局适配PC和移动设备
- 基于角色的动态导航菜单
- 简历上传与管理界面
- 职位推荐展示与详情查看
- 职位发布、编辑与管理功能
- 个人资料与通知设置管理
- 企业用户的职位管理
- 高级搜索与筛选功能
- 统一的UI组件与加载状态管理

### API接口

- 完整的RESTful API
- 自动生成的OpenAPI文档
- 速率限制和安全保护
- 详细的错误处理

## 错误处理和健壮性

系统实现了多层错误处理机制：

1. **服务级错误处理**：
   - 每个服务模块都有专门的错误捕获和恢复机制
   - 外部服务(如Weaviate)断开时的自动重连尝试

2. **API级错误处理**：
   - 所有API端点都有统一的错误响应格式
   - HTTP状态码和详细错误信息

3. **应用级错误处理**：
   - 全局异常处理中间件
   - 结构化日志记录所有系统错误

4. **前端错误处理**：
   - 全局网络请求错误处理
   - 请求取消和重试机制
   - 用户友好的错误提示

5. **保护机制**：
   - API速率限制防止滥用
   - 数据库事务保证一致性
   - 异步任务处理大型工作负载

## 最近更新

- 完善了前端组件结构，统一使用PageContentWrapper、SearchBox等组件
- 优化了加载状态管理，使用useLoading工具统一处理异步操作
- 实现了职位管理模块的编辑功能，完善职位发布流程
- 添加了简历技能提取和技能建议功能，增强简历分析能力
- 实现了推荐算法设置，支持调整技能权重和内容匹配权重
- 完善了个人中心，增加更多用户资料字段和通知设置
- 为职位市场和人才市场添加了高级搜索功能，支持多条件筛选
- 统一了用户界面风格，提升整体用户体验
- 优化了组件间通信和状态管理，使用Pinia存储解决方案

## 后续开发计划

- **推荐算法优化**：引入更先进的匹配算法，提高推荐准确性
- **数据分析功能**：添加招聘数据分析和可视化功能，帮助用户做出更好决策
- **实时通知系统**：实现基于WebSocket的实时通知功能
- **多语言支持**：增加多语言界面支持
- **移动应用开发**：开发配套的移动端应用
- **AI面试助手**：添加基于LLM的面试问题生成和评估工具
- **简历优化建议**：提供基于AI的简历改进建议
- **用户行为分析**：实现用户行为跟踪和个性化推荐

## 贡献指南

1. Fork项目仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式

项目维护者：AI招聘平台团队
邮箱：support@ai-recruitment.com 