# 快速开始指南

5分钟快速上手AutomationAPI！

## 第一步：安装和初始化

```bash
# 1. 进入项目目录
cd /Users/yzk/MyProjects/AutomationAPI

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Mac/Linux

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python manage.py migrate

# 5. 初始化API端点
python manage.py init_endpoints

# 6. 创建管理员账号
python manage.py createsuperuser
# 按提示输入用户名、邮箱和密码
```

## 第二步：配置微软应用（重要！）

在使用前，必须在Azure AD中注册应用并获取凭证：

### 注册Azure应用

1. 访问 [Azure Portal](https://portal.azure.com/)
2. 进入 **Azure Active Directory** → **应用注册** → **新注册**
3. 填写信息：
   - 名称：`AutomationAPI`
   - 支持的账户类型：选择适合的类型
4. 创建后记录：
   - **应用程序(客户端)ID**
   - **目录(租户)ID**
5. 进入 **证书和密码** → **新建客户端密码**，记录密码值

### 添加API权限

1. 进入 **API权限** → **添加权限** → **Microsoft Graph**
2. 选择 **应用程序权限**（非委托权限）
3. 添加以下权限：
   ```
   Mail.Send          # 发送邮件
   Mail.Read          # 读取邮件
   ChannelMessage.Send # 发送Teams消息
   Team.ReadBasic.All  # 读取Teams
   Sites.Read.All      # 读取SharePoint
   Sites.ReadWrite.All # 读写SharePoint
   ```
4. **授予管理员同意** ← 这一步必须完成！

## 第三步：启动服务

```bash
# 方式1：使用启动脚本（推荐）
./start.sh

# 方式2：手动启动
python manage.py runserver
```

服务启动后，访问：
- 🏠 主页：http://127.0.0.1:8000/
- 🔐 Admin：http://127.0.0.1:8000/admin/
- 📡 API：http://127.0.0.1:8000/api/

## 第四步：在Admin后台添加Token

1. 访问 http://127.0.0.1:8000/admin/
2. 使用刚才创建的管理员账号登录
3. 点击 **API Tokens** → **添加API TOKEN**
4. 填写信息：
   - **名称**：主Token（或任意名称）
   - **Client ID**：从Azure获取的应用程序ID
   - **Client Secret**：从Azure获取的客户端密码
   - **Tenant ID**：从Azure获取的目录ID
   - **是否启用**：✓ 勾选
5. 点击 **保存**

## 第五步：测试API

### 测试1：发送Teams消息

首先，获取Teams的团队ID和频道ID：

```bash
# 获取团队列表
curl -u admin:yourpassword http://127.0.0.1:8000/api/microsoft/list_teams/
```

然后发送消息：

```bash
curl -X POST http://127.0.0.1:8000/api/microsoft/send_teams_message/ \
  -u admin:yourpassword \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "channel",
    "team_id": "YOUR-TEAM-ID",
    "channel_id": "YOUR-CHANNEL-ID",
    "message": "Hello from AutomationAPI! 🎉"
  }'
```

### 测试2：发送邮件

```bash
curl -X POST http://127.0.0.1:8000/api/microsoft/send_email/ \
  -u admin:yourpassword \
  -H "Content-Type: application/json" \
  -d '{
    "to_recipients": ["your-email@example.com"],
    "subject": "测试邮件",
    "body": "<h1>成功！</h1><p>AutomationAPI运行正常</p>",
    "is_html": true
  }'
```

### 测试3：查看调用日志

```bash
# 查看所有日志
curl -u admin:yourpassword http://127.0.0.1:8000/api/logs/

# 查看统计数据
curl -u admin:yourpassword http://127.0.0.1:8000/api/logs/statistics/
```

## 常见问题

### Q1: Token显示"无效/过期"？
**A:** Token首次创建时是无效的，第一次调用API时会自动获取并缓存访问令牌。

### Q2: API调用返回"没有可用的API Token"？
**A:** 确保：
1. 已在Admin后台添加Token
2. Token的"是否启用"已勾选
3. Azure凭证填写正确

### Q3: 返回401或403错误？
**A:** 检查：
1. Azure应用权限是否已添加
2. 是否已"授予管理员同意"
3. Client Secret是否正确（注意有效期）

### Q4: Teams消息发送失败？
**A:** 
1. 确认已添加 `ChannelMessage.Send` 权限
2. 验证Team ID和Channel ID正确
3. 确保应用已添加到对应的Teams团队

### Q5: 如何获取Team ID和Channel ID？
**A:** 
```bash
# 方式1：使用API获取
curl -u admin:password http://127.0.0.1:8000/api/microsoft/list_teams/

# 方式2：从Teams URL中获取
# 打开Teams频道，URL格式：
# https://teams.microsoft.com/l/channel/CHANNEL-ID/...?groupId=TEAM-ID
```

## 下一步

### 查看完整文档
- 📖 [完整README](README.md) - 详细功能介绍
- 💻 [API示例](API_EXAMPLES.md) - 更多使用示例

### 在Admin后台探索
1. **API端点** - 查看所有可用的API端点
2. **使用日志** - 详细的调用记录和统计
3. **Teams消息模板** - 创建可复用的消息模板
4. **邮件模板** - 创建邮件模板

### Python集成

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"
AUTH = ("admin", "yourpassword")

# 发送Teams消息
response = requests.post(
    f"{BASE_URL}/microsoft/send_teams_message/",
    json={
        "message_type": "channel",
        "team_id": "your-team-id",
        "channel_id": "your-channel-id",
        "message": "自动化消息"
    },
    auth=AUTH
)
print(response.json())
```

## 需要帮助？

1. 查看Admin后台的使用日志，了解错误详情
2. 运行测试：`python manage.py test`
3. 查看[完整文档](README.md)
4. 检查Azure应用配置

祝使用愉快！🚀

