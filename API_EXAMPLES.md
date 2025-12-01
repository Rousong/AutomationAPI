# API使用示例

本文档提供AutomationAPI的详细使用示例。

## 认证

所有API请求都需要认证。使用Django的Session认证或基本认证。

### 使用curl进行认证

```bash
# 方式1：基本认证
curl -u username:password http://127.0.0.1:8000/api/

# 方式2：获取CSRF token后使用session
curl -c cookies.txt http://127.0.0.1:8000/admin/login/
```

## 1. Token管理API

### 1.1 列出所有Token

```bash
GET /api/tokens/

curl -u admin:password http://127.0.0.1:8000/api/tokens/
```

**响应示例：**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "主Token",
      "is_active": true,
      "is_valid": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 1.2 创建新Token

```bash
POST /api/tokens/

curl -X POST http://127.0.0.1:8000/api/tokens/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试Token",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "tenant_id": "your-tenant-id",
    "is_active": true
  }'
```

### 1.3 更新Token

```bash
PUT /api/tokens/1/

curl -X PUT http://127.0.0.1:8000/api/tokens/1/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新后的Token",
    "is_active": true
  }'
```

## 2. Teams API

### 2.1 发送频道消息

```bash
POST /api/microsoft/send_teams_message/

curl -X POST http://127.0.0.1:8000/api/microsoft/send_teams_message/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "channel",
    "team_id": "19:xxx@thread.tacv2",
    "channel_id": "19:yyy@thread.tacv2",
    "message": "Hello from AutomationAPI! 🚀"
  }'
```

**响应示例：**
```json
{
  "status": "success",
  "message": "Teams消息发送成功",
  "data": {
    "id": "1234567890",
    "createdDateTime": "2024-01-01T00:00:00Z"
  }
}
```

### 2.2 发送聊天消息

```bash
POST /api/microsoft/send_teams_message/

curl -X POST http://127.0.0.1:8000/api/microsoft/send_teams_message/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "chat",
    "chat_id": "19:zzz@thread.v2",
    "message": "这是一条聊天消息"
  }'
```

### 2.3 列出Teams团队

```bash
GET /api/microsoft/list_teams/

curl -u admin:password http://127.0.0.1:8000/api/microsoft/list_teams/
```

**响应示例：**
```json
{
  "status": "success",
  "data": {
    "value": [
      {
        "id": "team-id-1",
        "displayName": "开发团队",
        "description": "开发团队协作空间"
      }
    ]
  }
}
```

## 3. Outlook邮件API

### 3.1 发送邮件

```bash
POST /api/microsoft/send_email/

curl -X POST http://127.0.0.1:8000/api/microsoft/send_email/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "to_recipients": ["user1@example.com", "user2@example.com"],
    "cc_recipients": ["cc@example.com"],
    "subject": "AutomationAPI测试邮件",
    "body": "<h1>你好</h1><p>这是一封来自AutomationAPI的测试邮件。</p><ul><li>功能1</li><li>功能2</li></ul>",
    "is_html": true
  }'
```

### 3.2 纯文本邮件

```bash
curl -X POST http://127.0.0.1:8000/api/microsoft/send_email/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "to_recipients": ["user@example.com"],
    "subject": "纯文本邮件",
    "body": "这是一封纯文本邮件。",
    "is_html": false
  }'
```

### 3.3 获取邮件列表

```bash
GET /api/microsoft/list_emails/?folder=inbox&top=10

curl -u admin:password \
  "http://127.0.0.1:8000/api/microsoft/list_emails/?folder=inbox&top=10"
```

**响应示例：**
```json
{
  "status": "success",
  "data": {
    "value": [
      {
        "id": "message-id",
        "subject": "邮件主题",
        "from": {
          "emailAddress": {
            "address": "sender@example.com"
          }
        },
        "receivedDateTime": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

## 4. SharePoint API

### 4.1 获取站点信息

```bash
POST /api/microsoft/sharepoint_operation/

curl -X POST http://127.0.0.1:8000/api/microsoft/sharepoint_operation/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "get_site",
    "site_id": "contoso.sharepoint.com,site-id,web-id"
  }'
```

### 4.2 列出站点列表

```bash
curl -X POST http://127.0.0.1:8000/api/microsoft/sharepoint_operation/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "list_lists",
    "site_id": "your-site-id"
  }'
```

### 4.3 获取列表项

```bash
curl -X POST http://127.0.0.1:8000/api/microsoft/sharepoint_operation/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "get_items",
    "site_id": "your-site-id",
    "list_id": "your-list-id"
  }'
```

## 5. API端点管理

### 5.1 列出所有端点

```bash
GET /api/endpoints/

curl -u admin:password http://127.0.0.1:8000/api/endpoints/
```

### 5.2 按服务筛选

```bash
GET /api/endpoints/?service=teams

curl -u admin:password \
  "http://127.0.0.1:8000/api/endpoints/?service=teams"
```

### 5.3 获取端点统计

```bash
GET /api/endpoints/statistics/

curl -u admin:password \
  http://127.0.0.1:8000/api/endpoints/statistics/
```

**响应示例：**
```json
[
  {
    "service": "teams",
    "total_endpoints": 4,
    "active_endpoints": 4,
    "total_calls": 150
  },
  {
    "service": "outlook",
    "total_endpoints": 3,
    "active_endpoints": 3,
    "total_calls": 80
  }
]
```

## 6. 使用日志API

### 6.1 查看调用日志

```bash
GET /api/logs/

curl -u admin:password http://127.0.0.1:8000/api/logs/
```

### 6.2 按状态筛选

```bash
GET /api/logs/?status=success

curl -u admin:password \
  "http://127.0.0.1:8000/api/logs/?status=success"
```

### 6.3 按时间筛选（最近N天）

```bash
GET /api/logs/?days=7

curl -u admin:password \
  "http://127.0.0.1:8000/api/logs/?days=7"
```

### 6.4 获取使用统计

```bash
GET /api/logs/statistics/?days=30

curl -u admin:password \
  "http://127.0.0.1:8000/api/logs/statistics/?days=30"
```

**响应示例：**
```json
{
  "total_calls": 230,
  "success_calls": 215,
  "failed_calls": 10,
  "error_calls": 5,
  "by_endpoint": [
    {
      "endpoint__name": "Teams - 发送频道消息",
      "count": 100
    }
  ],
  "by_service": [
    {
      "endpoint__service": "teams",
      "count": 150
    }
  ]
}
```

## 7. Python示例

### 7.1 使用requests库

```python
import requests

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api"
AUTH = ("admin", "password")

# 发送Teams消息
def send_teams_message(team_id, channel_id, message):
    url = f"{BASE_URL}/microsoft/send_teams_message/"
    data = {
        "message_type": "channel",
        "team_id": team_id,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url, json=data, auth=AUTH)
    return response.json()

# 发送邮件
def send_email(recipients, subject, body):
    url = f"{BASE_URL}/microsoft/send_email/"
    data = {
        "to_recipients": recipients,
        "subject": subject,
        "body": body,
        "is_html": True
    }
    response = requests.post(url, json=data, auth=AUTH)
    return response.json()

# 获取使用统计
def get_statistics(days=7):
    url = f"{BASE_URL}/logs/statistics/"
    params = {"days": days}
    response = requests.get(url, params=params, auth=AUTH)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 发送消息
    result = send_teams_message(
        team_id="your-team-id",
        channel_id="your-channel-id",
        message="Hello from Python!"
    )
    print(f"消息发送结果: {result}")
    
    # 发送邮件
    result = send_email(
        recipients=["user@example.com"],
        subject="测试邮件",
        body="<h1>Hello</h1>"
    )
    print(f"邮件发送结果: {result}")
    
    # 获取统计
    stats = get_statistics(days=30)
    print(f"统计数据: {stats}")
```

## 8. 指定Token使用

默认情况下，系统会使用第一个活跃的Token。如果有多个Token，可以指定使用：

```bash
# 发送Teams消息时指定Token
curl -X POST http://127.0.0.1:8000/api/microsoft/send_teams_message/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "token_id": 2,
    "message_type": "channel",
    "team_id": "your-team-id",
    "channel_id": "your-channel-id",
    "message": "使用指定Token发送"
  }'
```

## 9. 错误处理

### 错误响应格式

```json
{
  "status": "error",
  "message": "详细的错误信息"
}
```

### 常见错误

**1. Token无效**
```json
{
  "status": "error",
  "message": "没有可用的API Token"
}
```

**2. 参数错误**
```json
{
  "message_type": ["频道消息需要提供team_id和channel_id"]
}
```

**3. 权限不足**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## 10. 批量操作示例

### 批量发送邮件

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"
AUTH = ("admin", "password")

# 批量发送
recipients_list = [
    {"email": "user1@example.com", "name": "用户1"},
    {"email": "user2@example.com", "name": "用户2"},
    {"email": "user3@example.com", "name": "用户3"},
]

for recipient in recipients_list:
    url = f"{BASE_URL}/microsoft/send_email/"
    data = {
        "to_recipients": [recipient["email"]],
        "subject": f"您好，{recipient['name']}",
        "body": f"<h1>欢迎 {recipient['name']}</h1>",
        "is_html": True
    }
    response = requests.post(url, json=data, auth=AUTH)
    print(f"发送给 {recipient['name']}: {response.json()}")
```

## 更多示例

访问项目的Admin后台，可以查看更多预配置的API端点和详细文档。

