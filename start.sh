#!/bin/bash
# 日程管理系统启动脚本
# 用法: ./start.sh [backend|frontend|seed|all]

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
UVI="$HOME/.local/bin/uvicorn"
PIP="$HOME/.local/bin/pip"

install_backend() {
    echo ">>> 安装后端依赖..."
    $PIP install -r "$ROOT/backend/requirements.txt" --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple -q
}

install_frontend() {
    echo ">>> 安装前端依赖..."
    cd "$ROOT/frontend" && npm install --silent
}

seed() {
    echo ">>> 插入种子数据..."
    cd "$ROOT/backend" && python3 seed.py
}

run_backend() {
    echo ">>> 启动后端 http://localhost:8001"
    echo "    API 文档: http://localhost:8001/docs"
    cd "$ROOT/backend" && $UVI app.main:app --host 0.0.0.0 --port 8001 --reload
}

run_frontend() {
    echo ">>> 启动前端 http://localhost:3000"
    cd "$ROOT/frontend" && npm run dev
}

case "${1:-all}" in
    backend)
        run_backend
        ;;
    frontend)
        run_frontend
        ;;
    seed)
        seed
        ;;
    install)
        install_backend
        install_frontend
        ;;
    all)
        install_backend
        install_frontend
        seed
        echo ""
        echo ">>> 启动后端 (后台) + 前端..."
        cd "$ROOT/backend" && $UVI app.main:app --host 0.0.0.0 --port 8001 &
        sleep 2
        cd "$ROOT/frontend" && npm run dev
        ;;
    *)
        echo "用法: ./start.sh [backend|frontend|seed|install|all]"
        ;;
esac
