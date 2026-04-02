#!/bin/bash

# 拓岳ERP启动脚本

echo "================================"
echo "  拓岳ERP系统启动脚本"
echo "================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -q -r requirements.txt

# 数据库迁移
echo "执行数据库迁移..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# 检查是否需要填充数据
python -c "
import django
django.setup()
from apps.tenants.models import Tenant
try:
    Tenant.objects.get(code='demo')
    print('数据已存在，跳过填充')
except Tenant.DoesNotExist:
    print('填充测试数据...')
    exec(open('seed_data.py').read())
"

echo ""
echo "================================"
echo "  启动开发服务器"
echo "================================"
echo "API文档: http://localhost:8000/api/docs/"
echo "管理员后台: http://localhost:8000/admin/"
echo ""
echo "登录账号: admin"
echo "登录密码: admin123"
echo "================================"

python manage.py runserver 0.0.0.0:8000
