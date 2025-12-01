#!/bin/bash
# AutomationAPI 启动脚本

echo "=================================="
echo "  AutomationAPI 启动脚本"
echo "=================================="
echo ""

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    echo "✓ 激活虚拟环境..."
    source venv/bin/activate
else
    echo "✗ 未找到虚拟环境，请先运行: python3 -m venv venv"
    exit 1
fi

# 检查数据库
if [ ! -f "db.sqlite3" ]; then
    echo "✓ 初始化数据库..."
    python manage.py migrate
    
    echo ""
    echo "✓ 初始化API端点..."
    python manage.py init_endpoints
    
    echo ""
    echo "请创建管理员账号："
    python manage.py createsuperuser
fi

echo ""
echo "✓ 启动开发服务器..."
echo ""
echo "访问地址："
echo "  - 主页: http://127.0.0.1:8000/"
echo "  - Admin: http://127.0.0.1:8000/admin/"
echo "  - API: http://127.0.0.1:8000/api/"
echo ""

python manage.py runserver

