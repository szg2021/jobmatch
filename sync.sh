#!/bin/bash

# 记录日志
LOG_FILE="/var/log/jobmatch/sync.log"
mkdir -p /var/log/jobmatch
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