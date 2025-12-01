# AutomationAPI - 微软API自动化管理系统

一个基于Django和Django REST Framework的微软API管理平台，用于统一管理和调用Microsoft Teams、Outlook、SharePoint等微软服务的API。

## 功能特性

- ✅ **Token管理**：在Admin后台统一管理微软API的认证密钥（Client ID、Client Secret、Tenant ID）
- ✅ **API端点管理**：预配置常用的微软API端点，支持自定义添加
- ✅ **使用统计**：详细记录每次API调用的日志，包括请求、响应、状态码、响应时间等
- ✅ **Teams集成**：发送频道消息、聊天消息，列出团队等
- ✅ **Outlook集成**：发送邮件、获取邮件列表等
- ✅ **SharePoint集成**：访问站点、列表、文档库，上传文件等
- ✅ **模板支持**：支持Teams消息模板和邮件模板，方便复用
- ✅ **RESTful API**：提供完整的REST API接口，易于集成

## 技术栈

- Django 4.2.11
- Django REST Framework 3.14.0
- Python 3.9+
- SQLite（可切换到其他数据库）

## 快速开始

### 1. 安装依赖

```bash
# 克隆项目
cd /Users/yzk/MyProjects/AutomationAPI

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

复制 `.env.example` 创建 `.env` 文件并配置：

```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Microsoft Graph API配置（可在Admin后台配置）
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
MICROSOFT_TENANT_ID=your-tenant-id
```

### 3. 初始化数据库

```bash
# 执行迁移
python manage.py migrate

# 初始化API端点
python manage.py init_endpoints

# 创建管理员账号
python manage.py createsuperuser
```

### 4. 启动服务

```bash
python manage.py runserver
```

访问：
- 主页：http://127.0.0.1:8000/
- Admin后台：http://127.0.0.1:8000/admin/
- API文档：http://127.0.0.1:8000/api/

## 微软应用注册

在使用本系统之前，需要在Azure AD中注册应用程序：

1. 登录 [Azure Portal](https://portal.azure.com/)
2. 进入 **Azure Active Directory** > **应用注册** > **新注册**
3. 配置应用：
   - 名称：AutomationAPI
   - 支持的账户类型：选择适合的类型
   - 重定向URI：可选
4. 创建后，记录：
   - **应用程序(客户端)ID** → `MICROSOFT_CLIENT_ID`
   - **目录(租户)ID** → `MICROSOFT_TENANT_ID`
5. 进入 **证书和密码** > **新建客户端密码**，记录：
   - **客户端密码的值** → `MICROSOFT_CLIENT_SECRET`
6. 进入 **API权限** > **添加权限** > **Microsoft Graph**，添加所需权限：
   - `Mail.Send`（发送邮件）
   - `Mail.Read`（读取邮件）
   - `ChannelMessage.Send`（发送Teams消息）
   - `Team.ReadBasic.All`（读取Teams）
   - `Sites.Read.All`（读取SharePoint站点）
   - `Sites.ReadWrite.All`（读写SharePoint）
   - 等等...
7. **授予管理员同意**

## API使用示例

### 1. 在Admin后台配置Token

1. 登录Admin后台：http://127.0.0.1:8000/admin/
2. 进入 **API Tokens** > **添加**
3. 填写Token信息：
   - 名称：主Token
   - Client ID：从Azure获取
   - Client Secret：从Azure获取
   - Tenant ID：从Azure获取
   - 是否启用：✓

### 2. 发送Teams消息

**API端点：** `POST /api/microsoft/send_teams_message/`

**请求示例：**

```bash
curl -X POST http://127.0.0.1:8000/api/microsoft/send_teams_message/ \
  -H "Content-Type: application/json" \
  -u username:password \
  -d '{
    "message_type": "channel",
    "team_id": "your-team-id",
    "channel_id": "your-channel-id",
    "message": "Hello from AutomationAPI!"
  }'
```

### 3. 发送邮件

**API端点：** `POST /api/microsoft/send_email/`

**请求示例：**

```bash
curl -X POST http://127.0.0.1:8000/api/microsoft/send_email/ \
  -H "Content-Type: application/json" \
  -u username:password \
  -d '{
    "to_recipients": ["user@example.com"],
    "subject": "测试邮件",
    "body": "<h1>Hello</h1><p>这是一封测试邮件</p>",
    "is_html": true
  }'
```

### 4. SharePoint操作

**API端点：** `POST /api/microsoft/sharepoint_operation/`

**请求示例（获取站点）：**

```bash
curl -X POST http://127.0.0.1:8000/api/microsoft/sharepoint_operation/ \
  -H "Content-Type: application/json" \
  -u username:password \
  -d '{
    "operation": "get_site",
    "site_id": "your-site-id"
  }'
```

## API端点列表

### Token管理
- `GET /api/tokens/` - 列出所有Token
- `POST /api/tokens/` - 创建Token
- `GET /api/tokens/{id}/` - 获取Token详情
- `PUT /api/tokens/{id}/` - 更新Token
- `DELETE /api/tokens/{id}/` - 删除Token

### 端点管理
- `GET /api/endpoints/` - 列出所有API端点
- `POST /api/endpoints/` - 创建端点
- `GET /api/endpoints/statistics/` - 获取端点统计

### 使用日志
- `GET /api/logs/` - 列出调用日志
- `GET /api/logs/{id}/` - 获取日志详情
- `GET /api/logs/statistics/` - 获取使用统计

### 微软API操作
- `POST /api/microsoft/send_teams_message/` - 发送Teams消息
- `POST /api/microsoft/send_email/` - 发送邮件
- `POST /api/microsoft/sharepoint_operation/` - SharePoint操作
- `GET /api/microsoft/list_teams/` - 列出Teams团队
- `GET /api/microsoft/list_emails/` - 列出邮件

### 模板管理
- `GET /api/teams-messages/` - Teams消息模板
- `GET /api/email-templates/` - 邮件模板

## Admin后台功能

### 1. API Token管理
- 添加、编辑、删除Token
- 查看Token状态（有效/过期）
- Token自动刷新机制

### 2. API端点管理
- 管理API端点配置
- 查看调用次数统计
- 启用/禁用端点

### 3. 使用日志查看
- 详细的API调用日志
- 按状态、端点、时间筛选
- 查看请求/响应详情
- 性能分析（响应时间）

### 4. 模板管理
- Teams消息模板
- 邮件模板
- 支持变量替换

## 项目结构

```
AutomationAPI/
├── automationapi/          # Django项目配置
│   ├── settings.py        # 项目设置
│   ├── urls.py            # 主URL配置
│   └── wsgi.py
├── microsoft_api/         # 微软API应用
│   ├── models.py          # 数据模型
│   ├── views.py           # API视图
│   ├── serializers.py     # 序列化器
│   ├── services.py        # 微软API服务类
│   ├── admin.py           # Admin配置
│   ├── urls.py            # URL路由
│   └── management/        # 管理命令
│       └── commands/
│           └── init_endpoints.py
├── manage.py
├── requirements.txt       # 依赖列表
└── README.md             # 本文档
```

## 开发说明

### 添加新的API端点

1. 在Admin后台添加端点配置
2. 在 `services.py` 中添加相应的方法
3. 在 `views.py` 中创建视图
4. 在 `serializers.py` 中创建序列化器（如需要）

### 扩展微软服务

继承 `MicrosoftGraphService` 类创建新的服务类：

```python
from .services import MicrosoftGraphService

class CustomService(MicrosoftGraphService):
    def custom_method(self, param, user=None):
        endpoint = "custom/endpoint"
        return self.make_request('GET', endpoint, user=user)
```

## 安全建议

1. **生产环境**：
   - 将 `DEBUG` 设置为 `False`
   - 使用强密码作为 `SECRET_KEY`
   - 配置 `ALLOWED_HOSTS`
   - 使用HTTPS
   
2. **Token安全**：
   - Client Secret只在Admin后台显示一次
   - API响应中不返回敏感信息
   - 定期更新Token
   
3. **权限控制**：
   - 所有API需要认证
   - 使用Django的权限系统
   - 记录所有API调用

## 故障排查

### Token无效或过期
- 检查Azure应用配置
- 检查Token是否启用
- 查看错误日志

### API调用失败
- 检查权限配置
- 查看调用日志中的错误信息
- 验证参数格式

### 无法访问某些资源
- 检查Azure AD中的API权限
- 确认已授予管理员同意
- 检查资源ID是否正确

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 支持

如有问题，请创建Issue或联系开发团队。