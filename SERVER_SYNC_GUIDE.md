# 云服务器代码同步指南

## 初始设置（首次操作）

1. 确保服务器已安装Git：
```bash
# 检查Git版本
git --version

# 如果未安装，则安装Git
sudo yum install -y git
```

2. 配置Git全局设置：
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

3. 在服务器上克隆代码仓库：
```bash
# 进入部署目录
cd /opt/jobmatch  # 或其他指定的部署目录

# 克隆仓库
git clone https://github.com/szg2021/jobmatch.git .

# 切换到development分支
git checkout development
```

## 日常同步操作

### 方法一：直接在服务器更新（推荐用于生产环境）

1. 在拉取更新前备份当前代码：
```bash
# 创建备份目录
mkdir -p /opt/backups/jobmatch
# 备份当前代码
tar -czf /opt/backups/jobmatch/backup-$(date +%Y%m%d_%H%M%S).tar.gz /opt/jobmatch/*
```

2. 拉取最新代码：
```bash
cd /opt/jobmatch
git fetch origin development
git reset --hard origin/development
```

3. 更新依赖和重新构建（如有更新）：
```bash
# 后端更新
cd backend
pip install -r requirements.txt
alembic upgrade head

# 前端更新
cd ../frontend
npm install
npm run build
```

4. 重启服务：
```bash
# 重启后端服务
sudo systemctl restart jobmatch_backend

# 重启Nginx（如果需要）
sudo systemctl restart nginx
```

### 方法二：使用分支管理（推荐用于测试环境）

1. 创建本地分支：
```bash
git checkout -b server-test
```

2. 拉取远程更新：
```bash
git fetch origin development
git merge origin/development
```

3. 如果有冲突，解决冲突后提交：
```bash
git add .
git commit -m "Merge development branch and resolve conflicts"
```

## 回滚操作（当更新出现问题时）

1. 使用Git回滚：
```bash
# 查看提交历史
git log --oneline

# 回滚到指定提交
git reset --hard <commit-hash>
```

2. 使用备份恢复：
```bash
# 停止服务
sudo systemctl stop jobmatch_backend
sudo systemctl stop nginx

# 恢复备份
cd /opt/backups/jobmatch
tar -xzf backup-[timestamp].tar.gz -C /

# 重启服务
sudo systemctl start jobmatch_backend
sudo systemctl start nginx
```

## 注意事项

1. 在进行代码同步前，始终确保已经备份了当前代码和数据库
2. 在生产环境中，建议使用固定的发布分支而不是开发分支
3. 确保服务器上的Git操作权限配置正确
4. 建议设置自动化脚本来执行同步操作
5. 保持良好的日志记录习惯，记录每次更新的内容和时间
6. 定期清理旧的备份文件以节省磁盘空间

## 自动化同步脚本示例

创建文件 `/opt/jobmatch/sync.sh`：
```bash
#!/bin/bash

# 记录日志
LOG_FILE="/var/log/jobmatch/sync.log"
echo "$(date): Starting code sync" >> $LOG_FILE

# 创建备份
BACKUP_DIR="/opt/backups/jobmatch"
BACKUP_FILE="backup-$(date +%Y%m%d_%H%M%S).tar.gz"
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/$BACKUP_FILE /opt/jobmatch/*

# 同步代码
cd /opt/jobmatch
git fetch origin development
git reset --hard origin/development

# 更新依赖
cd backend
pip install -r requirements.txt
alembic upgrade head

cd ../frontend
npm install
npm run build

# 重启服务
sudo systemctl restart jobmatch_backend
sudo systemctl restart nginx

echo "$(date): Code sync completed" >> $LOG_FILE
```

设置脚本权限：
```bash
chmod +x /opt/jobmatch/sync.sh
```

## 定时自动同步（可选）

添加定时任务：
```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨2点执行同步）
0 2 * * * /opt/jobmatch/sync.sh
``` 