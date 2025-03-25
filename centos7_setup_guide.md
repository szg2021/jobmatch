# CentOS 7.9 环境配置指南 - AI招聘推荐平台

本文档提供在CentOS 7.9服务器上部署AI招聘推荐平台所需的完整环境配置步骤。

## 1. 系统更新和基础工具

```bash
# 系统更新
sudo yum -y install epel-release
sudo yum -y update

# 安装基础开发工具
sudo yum groupinstall "Development Tools" -y
sudo yum install -y git curl wget vim zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel libffi-devel xz-devel
```

## 2. Python 3.10 安装 (从源码编译)

由于CentOS 7.9没有官方的Python 3.10软件包，我们需要从源码编译：

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

## 3. Node.js安装

### 选项1: 使用Node.js 16 (官方支持CentOS 7的最高版本)

```bash
# 安装Node.js 16 (CentOS 7兼容版本)
curl -fsSL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install -y nodejs

# 验证安装
node -v  # 应显示v16.x.x
npm -v
```

### 选项2: 使用Node.js 18的非官方构建版本 (由社区维护)

```bash
# 检查glibc版本
ldd --version  # CentOS 7.9通常是2.17

# 下载适用于glibc 2.17的Node.js 18
wget https://unofficial-builds.nodejs.org/download/release/v18.18.2/node-v18.18.2-linux-x64-glibc-217.tar.gz
sudo mkdir -p /usr/local/lib/nodejs
sudo tar -xzf node-v18.18.2-linux-x64-glibc-217.tar.gz -C /usr/local/lib/nodejs

# 设置环境变量
echo 'export PATH=/usr/local/lib/nodejs/node-v18.18.2-linux-x64-glibc-217/bin:$PATH' | sudo tee /etc/profile.d/nodejs.sh
source /etc/profile.d/nodejs.sh

# 验证安装
node -v  # 应显示v18.18.2
npm -v
```

## 4. 数据库安装

### PostgreSQL

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

# 配置远程访问(如需要)
sudo vi /var/lib/pgsql/14/data/postgresql.conf  # 修改listen_addresses = '*'
sudo vi /var/lib/pgsql/14/data/pg_hba.conf      # 添加 host all all 0.0.0.0/0 md5

# 重启服务
sudo systemctl restart postgresql-14
```

### Redis

```bash
# 安装Redis
sudo yum install -y redis

# 启动并设置开机自启
sudo systemctl enable redis
sudo systemctl start redis

# 验证安装
redis-cli ping  # 应返回PONG
```

## 5. Weaviate向量数据库 (使用Docker)

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
mkdir -p weaviate-data
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
      - ./weaviate-data:/var/lib/weaviate
EOF

# 启动Weaviate
sudo docker-compose up -d
```

## 6. 项目设置

### 创建项目目录并克隆代码

```bash
# 创建项目目录
mkdir -p /var/www/ai-recruitment
cd /var/www/ai-recruitment

# 克隆代码(如果已有Git仓库)
# git clone <repository-url> .

# 或者直接从本地上传代码(使用scp或其他方式)
```

### 后端设置

```bash
# 创建并激活虚拟环境
cd /var/www/ai-recruitment
python3.10 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 创建上传目录
mkdir -p uploads
```

### 前端设置

```bash
# 安装前端依赖
cd /var/www/ai-recruitment/frontend
npm install

# 构建前端(生产环境)
npm run build

# 或启动开发服务器
# npm run dev -- --host 0.0.0.0
```

## 7. Nginx配置

```bash
# 安装Nginx
sudo yum install -y nginx

# 启动Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# 创建网站配置
sudo vi /etc/nginx/conf.d/ai-recruitment.conf
```

配置文件内容：

```
server {
    listen 80;
    server_name your-server-ip;  # 替换为您的服务器IP或域名

    # 前端静态文件(生产环境)
    location / {
        root /var/www/ai-recruitment/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 或前端开发服务器(开发环境)
    # location / {
    #     proxy_pass http://localhost:5173;
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    #     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    # }

    # 后端API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 测试配置并重启Nginx
sudo nginx -t
sudo systemctl restart nginx
```

## 8. 进程管理 (使用PM2)

```bash
# 安装PM2
npm install -g pm2

# 创建启动脚本(后端)
cat > backend-start.sh << EOF
#!/bin/bash
cd /var/www/ai-recruitment
source venv/bin/activate
cd backend
python run.py
EOF

chmod +x backend-start.sh

# 使用PM2启动后端
pm2 start backend-start.sh --name "ai-recruitment-backend"

# 前端(如果使用开发服务器)
# cd /var/www/ai-recruitment/frontend
# pm2 start "npm run dev -- --host 0.0.0.0" --name "ai-recruitment-frontend"

# 设置PM2开机自启
pm2 startup
pm2 save
```

## 9. 防火墙配置

```bash
# 安装防火墙
sudo yum install -y firewalld

# 启动防火墙
sudo systemctl enable firewalld
sudo systemctl start firewalld

# 开放必要端口
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp  # 后端API
sudo firewall-cmd --permanent --add-port=5173/tcp  # 前端开发服务器(如需要)
sudo firewall-cmd --permanent --add-port=8080/tcp  # Weaviate
sudo firewall-cmd --reload

# 查看开放的端口
sudo firewall-cmd --list-all
```

## 10. 环境变量配置

```bash
# 创建.env文件
cat > /var/www/ai-recruitment/.env << EOF
# PostgreSQL
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=ai_recruitment
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Weaviate
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=

# 文档存储路径
DOCUMENT_STORAGE_PATH=./uploads
MAX_DOCUMENT_SIZE=10

# 安全设置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF
```

## 11. 系统监控与日志管理

```bash
# 安装日志管理工具
sudo yum install -y logrotate

# 配置日志轮转
sudo vi /etc/logrotate.d/ai-recruitment
```

配置文件内容：

```
/var/www/ai-recruitment/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 nginx nginx
}
```

## 12. 安全加固(可选)

```bash
# 安装fail2ban防止暴力破解
sudo yum install -y fail2ban

# 启动fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 配置fail2ban
sudo vi /etc/fail2ban/jail.local
```

配置文件内容：

```
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
```

```bash
# 重启fail2ban
sudo systemctl restart fail2ban
```

## 部署与启动指南

完成上述环境配置后，您可以按照以下步骤启动应用程序：

1. **启动后端**:
```bash
cd /var/www/ai-recruitment
source venv/bin/activate
cd backend
python run.py
```

2. **启动前端(开发模式)**:
```bash
cd /var/www/ai-recruitment/frontend
npm run dev -- --host 0.0.0.0
```

3. **或使用PM2管理进程**:
```bash
# 启动后端
pm2 start backend-start.sh --name "ai-recruitment-backend"

# 启动前端(开发模式)
cd /var/www/ai-recruitment/frontend
pm2 start "npm run dev -- --host 0.0.0.0" --name "ai-recruitment-frontend"

# 查看进程状态
pm2 status
```

## 特别注意事项

1. **Node.js版本兼容性**: CentOS 7.9与Node.js 18不直接兼容。建议使用Node.js 16.x或尝试非官方构建的Node.js 18(不保证所有功能都能正常工作)。

2. **Python 3.10编译时间**: 在CentOS 7.9上从源码编译Python 3.10可能需要较长时间，特别是在虚拟机或配置较低的服务器上。

3. **glibc版本限制**: CentOS 7.9使用较旧的glibc 2.17，这可能会限制某些需要更新版本的软件包。

4. **安全更新**: CentOS 7将于2024年6月30日结束维护生命周期(EOL)，仅提供有限的安全更新。建议长期规划中考虑迁移到更新的Linux发行版。

## 故障排除

1. **Python编译错误**:
   - 确保已安装所有必要的开发库
   - 尝试减少优化级别：使用 `./configure --with-ensurepip=install` 而不使用 `--enable-optimizations`

2. **PostgreSQL连接问题**:
   - 检查pg_hba.conf配置
   - 验证PostgreSQL服务是否运行：`sudo systemctl status postgresql-14`
   - 检查防火墙设置：`sudo firewall-cmd --list-all`

3. **Node.js相关错误**:
   - 如果使用Node.js 18遇到glibc错误，切换到Node.js 16
   - 检查npm全局模块路径权限

4. **Weaviate连接问题**:
   - 检查Docker服务状态：`sudo systemctl status docker`
   - 查看容器日志：`sudo docker logs weaviate` 