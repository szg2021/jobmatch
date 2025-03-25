# AI招聘推荐平台云服务器部署指南

本文档提供了AI招聘推荐平台在云服务器上的完整部署和测试指导。

## 一、服务器准备

### 1. 最低配置要求
- CPU: 2核心或以上
- 内存: 4GB或以上
- 磁盘空间: 20GB或以上
- 操作系统: CentOS 7.9或Ubuntu 20.04 LTS (推荐)

### 2. 域名和SSL (可选)
- 准备一个域名并完成DNS解析到服务器IP
- 获取SSL证书用于HTTPS连接

## 二、服务器基础环境配置

### 1. 系统更新和基础工具安装 (以CentOS 7.9为例)

```bash
# 更新系统
sudo yum -y install epel-release
sudo yum -y update

# 安装基础开发工具
sudo yum groupinstall "Development Tools" -y
sudo yum install -y git curl wget vim zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel libffi-devel xz-devel
```

### 2. Python 3.10安装

```bash
# 下载Python 3.10源码
wget https://www.python.org/ftp/python/3.10.9/Python-3.10.9.tgz
tar -xf Python-3.10.9.tgz
cd Python-3.10.9

# 配置和编译
./configure --enable-optimizations --with-ensurepip=install
sudo make altinstall  # 使用altinstall避免覆盖系统Python

# 验证安装
python3.10 --version
pip3.10 --version

# 创建软链接(可选)
sudo ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3
sudo ln -sf /usr/local/bin/pip3.10 /usr/local/bin/pip3

# 回到上一级目录
cd ..
```

### 3. Node.js安装

```bash
# 安装Node.js 16 (CentOS 7兼容版本)
curl -fsSL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install -y nodejs

# 验证安装
node -v  # 应显示v16.x.x
npm -v
```

### 4. PostgreSQL数据库安装

```bash
# 添加PostgreSQL官方源
sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# 安装PostgreSQL 14
sudo yum install -y postgresql14-server postgresql14-contrib

# 初始化数据库
sudo /usr/pgsql-14/bin/postgresql-14-setup initdb

# 启动并设置开机自启
sudo systemctl enable postgresql-14
sudo systemctl start postgresql-14

# 设置密码
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'your_secure_password';"

# 创建应用程序数据库和用户
sudo -u postgres psql -c "CREATE DATABASE jobmatch;"
sudo -u postgres psql -c "CREATE USER jobmatch_user WITH PASSWORD 'your_db_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE jobmatch TO jobmatch_user;"
```

### 5. Redis安装

```bash
# 安装Redis
sudo yum install -y redis

# 启动并设置开机自启
sudo systemctl enable redis
sudo systemctl start redis

# 验证安装
redis-cli ping  # 应返回PONG
```

### 6. Weaviate向量数据库安装 (使用Docker)

```bash
# 安装Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker
sudo systemctl enable docker
sudo systemctl start docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 创建Weaviate配置
mkdir -p /opt/weaviate
cd /opt/weaviate

cat > docker-compose.yml << EOF
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:1.18.3
    ports:
      - "8080:8080"
    restart: on-failure:0
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
      ENABLE_MODULES: ''
      CLUSTER_HOSTNAME: 'node1'
    volumes:
      - ./data:/var/lib/weaviate
EOF

# 启动Weaviate
sudo docker-compose up -d
```

## 三、项目部署

### 1. 代码获取

#### 方法A：从Git仓库克隆 (如果有)
```bash
# 创建项目目录
sudo mkdir -p /opt/jobmatch
sudo chown -R $(whoami):$(whoami) /opt/jobmatch
cd /opt/jobmatch

# 克隆项目仓库
git clone <repository-url> .
```

#### 方法B：通过文件上传
```bash
# 在本地打包项目
tar -czf jobmatch.tar.gz /path/to/your/project

# 使用scp上传到服务器
scp jobmatch.tar.gz user@your-server-ip:/tmp

# 在服务器上解压
sudo mkdir -p /opt/jobmatch
sudo chown -R $(whoami):$(whoami) /opt/jobmatch
cd /opt/jobmatch
tar -xzf /tmp/jobmatch.tar.gz
```

### 2. 后端配置与部署

```bash
# 进入项目目录
cd /opt/jobmatch

# 创建Python虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r backend/requirements.txt

# 创建.env文件
cat > backend/.env << EOF
# 数据库配置
USE_SQLITE=false
DATABASE_URL=postgresql://jobmatch_user:your_db_password@localhost/jobmatch

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# Weaviate配置
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=

# 安全配置
SECRET_KEY=$(openssl rand -hex 32)
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost", "http://localhost:80", "http://$(hostname -I | awk '{print $1}')"]

# 文档存储路径
DOCUMENT_STORAGE_PATH=./uploads
MAX_DOCUMENT_SIZE=10
EOF

# 创建上传目录
mkdir -p backend/uploads

# 数据库迁移
cd backend
alembic upgrade head
```

### 3. 前端配置与构建

```bash
# 进入前端目录
cd /opt/jobmatch/frontend

# 安装依赖
npm install

# 创建生产环境配置
cat > .env.production << EOF
VITE_APP_API_BASE_URL=/api
VITE_APP_TITLE=AI招聘推荐平台
VITE_APP_ENV=production
EOF

# 构建前端
npm run build
```

### 4. Nginx安装与配置

```bash
# 安装Nginx
sudo yum install -y nginx

# 创建网站配置
sudo vi /etc/nginx/conf.d/jobmatch.conf
```

将以下内容添加到配置文件中:

```nginx
server {
    listen 80;
    server_name your_server_ip_or_domain;  # 替换为您的服务器IP或域名

    # 前端静态文件
    location / {
        root /opt/jobmatch/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 上传文件访问
    location /uploads/ {
        alias /opt/jobmatch/backend/uploads/;
    }
}
```

```bash
# 测试配置并重启Nginx
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### 5. 使用Supervisor管理后端进程

```bash
# 安装Supervisor
sudo yum install -y supervisor

# 启动并启用Supervisor
sudo systemctl enable supervisord
sudo systemctl start supervisord

# 创建后端应用配置
sudo vi /etc/supervisord.d/jobmatch.ini
```

将以下内容添加到配置文件中:

```ini
[program:jobmatch]
directory=/opt/jobmatch/backend
command=/opt/jobmatch/venv/bin/python startup.py
user=root
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/jobmatch/backend.err.log
stdout_logfile=/var/log/jobmatch/backend.out.log
environment=PYTHONPATH=/opt/jobmatch
```

```bash
# 创建日志目录
sudo mkdir -p /var/log/jobmatch

# 重新加载Supervisor配置
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start jobmatch
```

### 6. 防火墙配置

```bash
# 开放必要端口
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 四、部署后测试

### 1. 检查服务状态

```bash
# 检查后端状态
sudo supervisorctl status jobmatch

# 检查Nginx状态
sudo systemctl status nginx

# 检查数据库状态
sudo systemctl status postgresql-14

# 检查Redis状态
sudo systemctl status redis

# 检查Weaviate状态
sudo docker ps | grep weaviate
```

### 2. 测试API连接

```bash
# 测试健康检查API
curl http://localhost:8000/api/health
```

### 3. 测试推荐系统

```bash
# 进入项目目录并激活虚拟环境
cd /opt/jobmatch
source venv/bin/activate

# 运行推荐测试脚本
cd backend
python -m scripts.test_recommendation_flow
```

### 4. 测试初始数据导入

```bash
# 从Python解释器调用初始化服务
cd /opt/jobmatch
source venv/bin/activate

python -c "import asyncio; from app.services.init_data import init_data; from app.db.session import SessionLocal; db = SessionLocal(); asyncio.run(init_data(db)); db.close()"
```

### 5. 网站功能测试

1. 打开浏览器访问 `http://your_server_ip_or_domain`
2. 测试用户注册功能
3. 测试用户登录功能
4. 上传简历或职位信息测试文档处理功能
5. 测试推荐功能
6. 检查系统日志是否有错误

## 五、问题排查

### 1. 后端服务无法启动

检查Supervisor日志:
```bash
sudo tail -f /var/log/jobmatch/backend.err.log
```

常见问题解决方案:
- 数据库连接问题: 确认PostgreSQL服务正在运行，检查连接信息是否正确
- 依赖问题: 确认所有Python依赖已正确安装
- 端口占用: 确认8000端口未被其他服务占用

### 2. 前端无法访问或显示错误

检查Nginx日志:
```bash
sudo tail -f /var/log/nginx/error.log
```

常见问题解决方案:
- 静态文件路径错误: 确认Nginx配置中的前端路径正确
- API请求失败: 检查浏览器开发者工具中的网络请求
- CORS问题: 确认后端的CORS配置包含前端域名

### 3. 推荐系统不工作

检查向量搜索服务:
```bash
# 检查Weaviate状态
curl http://localhost:8080/v1/.well-known/ready
```

测试推荐系统初始化:
```bash
# 手动触发向量搜索服务初始化
cd /opt/jobmatch
source venv/bin/activate
python -c "import asyncio; from app.services.recommendation_service import initialize_vector_search; from app.db.session import SessionLocal; db = SessionLocal(); asyncio.run(initialize_vector_search(db)); db.close()"

# 手动触发LightFM模型训练
python -c "import asyncio; from app.services.lightfm_recommendation_service import prepare_and_train_lightfm; from app.db.session import SessionLocal; from app.crud.crud_recommendation_config import recommendation_config; db = SessionLocal(); config = recommendation_config.get_active_config(db); asyncio.run(prepare_and_train_lightfm(db, config)); db.close()"
```

## 六、自动化监控与维护

### 1. 设置自动备份

```bash
# 创建备份脚本
cat > /opt/jobmatch/backup.sh << EOF
#!/bin/bash
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/var/backups/jobmatch

# 创建备份目录
mkdir -p \$BACKUP_DIR

# 备份数据库
sudo -u postgres pg_dump jobmatch > \$BACKUP_DIR/jobmatch_db_\$TIMESTAMP.sql

# 备份上传文件
tar -czf \$BACKUP_DIR/uploads_\$TIMESTAMP.tar.gz /opt/jobmatch/backend/uploads

# 保留最近7天的备份
find \$BACKUP_DIR -name "jobmatch_db_*.sql" -type f -mtime +7 -delete
find \$BACKUP_DIR -name "uploads_*.tar.gz" -type f -mtime +7 -delete
EOF

chmod +x /opt/jobmatch/backup.sh

# 添加到crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/jobmatch/backup.sh") | crontab -
```

### 2. 设置日志轮转

```bash
sudo vi /etc/logrotate.d/jobmatch
```

将以下内容添加到配置文件中:

```
/var/log/jobmatch/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
}
```

### 3. 系统监控设置 (可选)

使用简单的监控工具如Monit:

```bash
# 安装Monit
sudo yum install -y monit

# 配置Monit
sudo vi /etc/monit.conf
```

将以下内容添加到配置文件中:

```
set daemon 60
set log /var/log/monit.log
set idfile /var/lib/monit/id
set statefile /var/lib/monit/state

# Nginx监控
check process nginx with pidfile /var/run/nginx.pid
    start program = "/bin/systemctl start nginx"
    stop program = "/bin/systemctl stop nginx"
    if failed host 127.0.0.1 port 80 protocol http then restart

# PostgreSQL监控
check process postgresql with pidfile /var/run/postgresql/12-main.pid
    start program = "/bin/systemctl start postgresql-14"
    stop program = "/bin/systemctl stop postgresql-14"
    if failed host 127.0.0.1 port 5432 protocol postgresql then restart

# Backend应用监控
check process jobmatch with pidfile /var/run/supervisor/supervisord.pid
    start program = "/bin/systemctl start supervisord"
    stop program = "/bin/systemctl stop supervisord"
    if failed port 8000 type tcp then restart
```

```bash
# 启动Monit
sudo systemctl enable monit
sudo systemctl start monit
```

## 七、完整性测试清单

部署完成后，使用以下清单确保所有功能正常工作:

1. **基础功能**
   - [ ] 网站可通过IP或域名访问
   - [ ] 用户可以注册新账号
   - [ ] 用户可以登录
   - [ ] 用户可以重置密码

2. **求职者功能**
   - [ ] 上传简历
   - [ ] 查看简历解析结果
   - [ ] 查看推荐职位
   - [ ] 为推荐结果提供反馈

3. **企业功能**
   - [ ] 发布新职位
   - [ ] 管理已发布职位
   - [ ] 查看推荐简历
   - [ ] 为推荐结果提供反馈

4. **管理员功能**
   - [ ] 访问管理界面
   - [ ] 查看系统状态
   - [ ] 管理用户账号
   - [ ] 查看系统日志

5. **推荐系统**
   - [ ] 验证向量搜索服务可用
   - [ ] 验证LightFM模型训练成功
   - [ ] 测试职位推荐功能准确性
   - [ ] 测试简历推荐功能准确性

## 八、性能优化建议

1. **数据库优化**
   - 为常用查询添加适当的索引
   - 定期维护数据库(VACUUM, ANALYZE)
   - 考虑使用连接池

2. **推荐系统优化**
   - 实施推荐结果缓存
   - 批量处理数据更新
   - 调整向量维度和搜索参数

3. **前端性能**
   - 启用Nginx的gzip压缩
   - 设置适当的静态资源缓存策略
   - 考虑使用CDN加速静态资源

## 九、故障恢复

### 1. 数据库恢复

```bash
# 从备份恢复数据库
sudo -u postgres psql jobmatch < /var/backups/jobmatch/jobmatch_db_YYYYMMDD_HHMMSS.sql
```

### 2. 文件恢复

```bash
# 从备份恢复上传文件
tar -xzf /var/backups/jobmatch/uploads_YYYYMMDD_HHMMSS.tar.gz -C /
```

### 3. 服务重启

```bash
# 重启所有服务
sudo systemctl restart postgresql-14
sudo systemctl restart redis
sudo supervisorctl restart jobmatch
sudo systemctl restart nginx
sudo docker restart weaviate
``` 