#!/bin/bash
# ============================================================
# 老铛的创世区块 — 一键部署脚本
# 适用于 Alibaba Cloud Linux 4 / CentOS / RHEL
# 用法: bash deploy.sh
# ============================================================
set -e

SERVER_IP="你的服务器IP"
APP_DIR="/opt/laodang"

echo "========================================"
echo "  老铛的创世区块 — 服务器部署"
echo "========================================"
echo ""

# ── 1. 安装系统依赖 ──
echo "[1/5] 安装 Python 和 pip..."
dnf install -y python3 python3-pip 2>/dev/null || yum install -y python3 python3-pip

# ── 2. 创建应用目录 ──
echo "[2/5] 准备目录..."
mkdir -p $APP_DIR/data $APP_DIR/uploads $APP_DIR/templates/admin

# ── 3. 上传代码 ──
echo "[3/5] 安装 Python 依赖..."
pip3 install -r $APP_DIR/requirements.txt

# ── 4. 初始化数据库 ──
echo "[4/5] 初始化数据库..."
cd $APP_DIR
python3 seed.py

# ── 5. 配置 systemd 服务 ──
echo "[5/5] 配置开机自启..."
cp $APP_DIR/laodang.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable laodang
systemctl restart laodang

# ── 检查防火墙 ──
echo ""
echo "检查防火墙..."
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --add-port=8080/tcp --permanent 2>/dev/null || true
    firewall-cmd --reload 2>/dev/null || true
    echo "  已开放 8080 端口"
fi

echo ""
echo "========================================"
echo "  部署完成！"
echo "  访问: http://$SERVER_IP:8080"
echo "  后台: http://$SERVER_IP:8080/admin"
echo "========================================"
echo ""
echo "常用命令:"
echo "  查看状态: systemctl status laodang"
echo "  查看日志: journalctl -u laodang -f"
echo "  重启服务: systemctl restart laodang"
echo "  停止服务: systemctl stop laodang"
