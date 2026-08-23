#!/usr/bin/env bash
# 注塑机智能问答系统备份脚本
# 用法：在部署服务器项目根目录执行 ./deploy/backup.sh
set -euo pipefail

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "=== 备份数据库 ==="
docker compose exec -T db pg_dump -U aiqa aiqa > "$BACKUP_DIR/db_$TIMESTAMP.sql"

echo "=== 备份附件 ==="
docker compose exec -T backend tar czf - -C /data uploads > "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" 2>/dev/null || \
  echo "（附件目录为空或不存在，跳过）"

echo "=== 完成 ==="
ls -lh "$BACKUP_DIR"
