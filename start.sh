#!/bin/bash
# 拓岳 ERP 快速启动脚本

echo "🚀 拓岳 ERP 启动脚本"
echo "===================="

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误：请在 tuoyue-erp 项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo ""
echo "📦 启动 Django 后端..."
cd backend
source venv/bin/activate 2>/dev/null || echo "⚠️ 请手动激活虚拟环境: source venv/bin/activate"
python manage.py migrate --check 2>/dev/null || python manage.py migrate
echo "✅ 后端迁移完成"

# 检查是否需要生成测试数据
echo ""
read -p "📝 是否生成测试数据? (y/n): " gen_data
if [ "$gen_data" = "y" ]; then
    python scripts/generate_test_data.py
fi

# 启动后端服务
echo ""
echo "🌐 启动后端服务 (http://localhost:8000)..."
python manage.py runserver &
BACKEND_PID=$!

cd ..

# 启动前端
echo ""
echo "📱 启动 Vue3 前端..."
cd frontend
echo "🌐 启动前端服务 (http://localhost:5173)..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✨ 拓岳 ERP 已启动!"
echo "===================="
echo "前端地址: http://localhost:5173"
echo "后端地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/api/docs/"
echo ""
echo "登录信息:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait