# 部署指南

本文档提供AutomationAPI的部署说明和最佳实践。

## 开发环境部署

### 快速启动

```bash
# 1. 克隆并进入项目
cd /Users/yzk/MyProjects/AutomationAPI

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python manage.py migrate
python manage.py init_endpoints

# 5. 创建管理员
python manage.py createsuperuser

# 6. 启动开发服务器
python manage.py runserver
# 或使用启动脚本: ./start.sh
```

## 生产环境部署

### 1. 环境准备

#### 系统要求
- Python 3.9+
- PostgreSQL 12+ 或 MySQL 8+ （推荐）
- Nginx
- Supervisor 或 systemd

#### 安装依赖
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install postgresql postgresql-contrib
sudo apt install nginx
sudo apt install supervisor

# 或使用Docker
# 参考Docker部署章节
```

### 2. 配置数据库

#### PostgreSQL配置

```bash
# 创建数据库和用户
sudo -u postgres psql

CREATE DATABASE automationapi;
CREATE USER automationapi_user WITH PASSWORD 'strong_password';
ALTER ROLE automationapi_user SET client_encoding TO 'utf8';
ALTER ROLE automationapi_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE automationapi_user SET timezone TO 'Asia/Shanghai';
GRANT ALL PRIVILEGES ON DATABASE automationapi TO automationapi_user;
\q
```

#### 更新requirements.txt
```bash
# 添加PostgreSQL支持
echo "psycopg2-binary==2.9.9" >> requirements.txt
pip install psycopg2-binary
```

#### 配置Django使用PostgreSQL

创建 `.env` 文件：
```env
SECRET_KEY=生成一个强密钥
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=automationapi
DATABASE_USER=automationapi_user
DATABASE_PASSWORD=strong_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
MICROSOFT_TENANT_ID=your-tenant-id
```

更新 `settings.py`（如果使用环境变量）：
```python
DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DATABASE_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DATABASE_USER', default=''),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default=''),
        'PORT': config('DATABASE_PORT', default=''),
    }
}
```

### 3. 配置Gunicorn

#### 安装Gunicorn
```bash
pip install gunicorn
```

#### 创建Gunicorn配置文件
```bash
# gunicorn_config.py
bind = '127.0.0.1:8000'
workers = 4
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = '/var/log/automationapi/gunicorn_error.log'
accesslog = '/var/log/automationapi/gunicorn_access.log'
loglevel = 'info'
```

#### 创建systemd服务
```bash
# /etc/systemd/system/automationapi.service
[Unit]
Description=AutomationAPI Gunicorn daemon
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/AutomationAPI
Environment="PATH=/path/to/AutomationAPI/venv/bin"
ExecStart=/path/to/AutomationAPI/venv/bin/gunicorn \
          --config gunicorn_config.py \
          automationapi.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl start automationapi
sudo systemctl enable automationapi
sudo systemctl status automationapi
```

### 4. 配置Nginx

#### 创建Nginx配置
```nginx
# /etc/nginx/sites-available/automationapi

upstream automationapi {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 日志
    access_log /var/log/nginx/automationapi_access.log;
    error_log /var/log/nginx/automationapi_error.log;
    
    # 最大上传大小
    client_max_body_size 10M;
    
    # 静态文件
    location /static/ {
        alias /path/to/AutomationAPI/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 代理到Gunicorn
    location / {
        proxy_pass http://automationapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

#### 启用配置
```bash
sudo ln -s /etc/nginx/sites-available/automationapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. 收集静态文件

```bash
# 更新settings.py
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 收集静态文件
python manage.py collectstatic --noinput
```

### 6. 安全配置

#### 生成SECRET_KEY
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

#### 更新settings.py
```python
# 生产环境设置
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# HTTPS设置
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 其他安全设置
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
```

### 7. 日志配置

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/automationapi/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Docker部署

### Dockerfile

```dockerfile
FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制项目
COPY . /app/

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "automationapi.wsgi:application"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=automationapi
      - POSTGRES_USER=automationapi_user
      - POSTGRES_PASSWORD=strong_password
    restart: always

  web:
    build: .
    command: gunicorn automationapi.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    restart: always

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  static_volume:
```

### 启动Docker
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py init_endpoints
docker-compose exec web python manage.py createsuperuser
```

## 部署检查清单

### 部署前
- [ ] 设置强密码的SECRET_KEY
- [ ] DEBUG = False
- [ ] 配置ALLOWED_HOSTS
- [ ] 配置数据库
- [ ] 配置静态文件
- [ ] 添加环境变量
- [ ] 配置日志

### 安全检查
- [ ] 启用HTTPS
- [ ] 配置SSL证书
- [ ] 设置安全headers
- [ ] 限制管理员访问IP（可选）
- [ ] 配置防火墙
- [ ] 定期备份数据库

### 性能优化
- [ ] 配置数据库连接池
- [ ] 启用静态文件缓存
- [ ] 配置CDN（可选）
- [ ] 监控系统资源
- [ ] 配置日志轮转

### 监控
- [ ] 设置错误通知
- [ ] 配置性能监控
- [ ] 设置备份计划
- [ ] 监控API使用情况

## 维护

### 定期任务

#### 清理旧日志
```python
# management/commands/cleanup_logs.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from microsoft_api.models import APIUsageLog

class Command(BaseCommand):
    help = '清理30天前的日志'
    
    def handle(self, *args, **options):
        date_threshold = timezone.now() - timedelta(days=30)
        deleted = APIUsageLog.objects.filter(
            created_at__lt=date_threshold
        ).delete()
        self.stdout.write(
            self.style.SUCCESS(f'删除了 {deleted[0]} 条日志')
        )
```

#### 设置cron任务
```bash
# 每天凌晨2点清理日志
0 2 * * * cd /path/to/AutomationAPI && venv/bin/python manage.py cleanup_logs
```

### 备份

#### 数据库备份
```bash
# PostgreSQL
pg_dump -U automationapi_user automationapi > backup_$(date +%Y%m%d).sql

# 自动备份脚本
#!/bin/bash
BACKUP_DIR="/backups/automationapi"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U automationapi_user automationapi | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

### 更新

```bash
# 1. 备份数据库
pg_dump automationapi > backup_before_update.sql

# 2. 拉取最新代码
git pull origin main

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 更新依赖
pip install -r requirements.txt

# 5. 执行迁移
python manage.py migrate

# 6. 收集静态文件
python manage.py collectstatic --noinput

# 7. 重启服务
sudo systemctl restart automationapi
```

## 监控和日志

### 监控工具推荐
- **Sentry** - 错误追踪
- **Prometheus + Grafana** - 性能监控
- **ELK Stack** - 日志分析

### 查看日志
```bash
# Gunicorn日志
tail -f /var/log/automationapi/gunicorn_error.log

# Django日志
tail -f /var/log/automationapi/django.log

# Nginx日志
tail -f /var/log/nginx/automationapi_access.log

# systemd日志
journalctl -u automationapi -f
```

## 故障排查

### 服务无法启动
```bash
# 检查服务状态
sudo systemctl status automationapi

# 查看详细日志
journalctl -u automationapi -n 100

# 检查配置
python manage.py check --deploy
```

### 数据库连接失败
```bash
# 测试数据库连接
python manage.py dbshell

# 检查PostgreSQL状态
sudo systemctl status postgresql
```

### 静态文件404
```bash
# 重新收集静态文件
python manage.py collectstatic --clear --noinput

# 检查Nginx配置
sudo nginx -t
```

## 扩展建议

### 水平扩展
- 使用负载均衡器（如HAProxy）
- 部署多个Gunicorn实例
- 使用Redis缓存
- 配置读写分离数据库

### 缓存策略
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## 支持

遇到问题？
1. 查看[完整文档](README.md)
2. 检查[快速开始指南](QUICKSTART.md)
3. 查看日志文件
4. 运行 `python manage.py check --deploy`

---

**祝部署顺利！** 🚀

