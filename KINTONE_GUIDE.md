# Kintone API集成指南

AutomationAPI现已集成Kintone API，可以方便地管理和调用Kintone应用的数据。

## 什么是Kintone？

Kintone是一个日本的云端数据库平台，允许用户无需编程即可创建业务应用程序。通过AutomationAPI，您可以轻松地与Kintone进行集成。

## 功能特性

### ✅ 核心功能

- **连接管理** - 支持多个Kintone环境配置
- **双重认证** - 支持密码认证和API Token认证
- **应用管理** - 管理多个Kintone应用配置
- **完整CRUD** - 获取、添加、更新、删除记录
- **批量操作** - 支持批量添加和更新记录
- **字段映射** - 字段映射配置，便于系统集成
- **详细日志** - 记录所有API调用历史
- **来宾空间** - 支持Kintone来宾空间

### ✅ 支持的操作

1. **记录操作**
   - 获取记录列表（支持查询条件）
   - 获取单条记录
   - 添加单条记录
   - 批量添加记录
   - 更新单条记录
   - 批量更新记录
   - 删除记录

2. **应用信息**
   - 获取应用信息
   - 获取表单字段配置
   - 文件上传

## 快速开始

### 1. 配置Kintone连接

#### 在Admin后台配置

1. 登录 http://127.0.0.1:8000/admin/
2. 进入 **Kintone连接** → **添加**
3. 填写连接信息：

**基本信息：**
- 连接名称：主Kintone环境
- 子域名：your-company（不含.cybozu.com）
- 是否启用：✓

**认证配置：**

**方式1：API Token认证（推荐）**
- 认证方式：API Token认证
- API Token：从Kintone应用设置中获取

**方式2：密码认证**
- 认证方式：密码认证
- 用户名：your-username
- 密码：your-password

4. 保存

### 2. 获取Kintone API Token

#### 在Kintone中生成API Token

1. 登录Kintone：https://your-company.cybozu.com
2. 打开要访问的应用
3. 点击设置图标 → **应用设置**
4. 进入 **设置** → **API Token**
5. 点击 **生成**
6. 设置访问权限：
   - ✓ 查看记录
   - ✓ 添加记录
   - ✓ 编辑记录
   - ✓ 删除记录
7. 保存设置
8. **重要：更新应用**（应用设置必须更新才能生效）
9. 复制API Token到AutomationAPI

### 3. 配置Kintone应用

1. 在Admin后台进入 **Kintone应用** → **添加**
2. 填写：
   - 连接：选择刚创建的连接
   - 应用ID：从Kintone URL获取（例如：123）
   - 应用名称：客户管理
   - 描述：客户信息管理应用
3. 保存

### 4. 测试API

#### 获取记录

```bash
curl -X POST http://127.0.0.1:8000/api/kintone/kintone/get_records/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123",
    "query": "客户名称 like \"测试\"",
    "total_count": true
  }'
```

## API使用示例

### 1. 获取记录列表

```bash
POST /api/kintone/kintone/get_records/

curl -X POST http://127.0.0.1:8000/api/kintone/kintone/get_records/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123",
    "query": "更新日期 > \"2024-01-01\"",
    "fields": ["记录编号", "客户名称", "联系电话"],
    "total_count": true
  }'
```

**响应示例：**
```json
{
  "status": "success",
  "message": "记录获取成功",
  "data": {
    "records": [
      {
        "记录编号": {"value": "1"},
        "客户名称": {"value": "测试公司"},
        "联系电话": {"value": "1234567890"}
      }
    ],
    "totalCount": "1"
  }
}
```

### 2. 获取单条记录

```bash
POST /api/kintone/kintone/get_record/

curl -X POST http://127.0.0.1:8000/api/kintone/kintone/get_record/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123",
    "record_id": "1"
  }'
```

### 3. 添加记录

```bash
POST /api/kintone/kintone/add_record/

curl -X POST http://127.0.0.1:8000/api/kintone/kintone/add_record/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123",
    "record_data": {
      "客户名称": {"value": "新客户"},
      "联系电话": {"value": "9876543210"},
      "邮箱": {"value": "customer@example.com"}
    }
  }'
```

**响应示例：**
```json
{
  "status": "success",
  "message": "记录添加成功",
  "data": {
    "id": "2",
    "revision": "1"
  }
}
```

### 4. 批量添加记录

```bash
POST /api/kintone/kintone/add_records/

curl -X POST http://127.0.0.1:8000/api/kintone/kintone/add_records/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123",
    "records_data": [
      {
        "客户名称": {"value": "客户A"},
        "联系电话": {"value": "1111111111"}
      },
      {
        "客户名称": {"value": "客户B"},
        "联系电话": {"value": "2222222222"}
      }
    ]
  }'
```

### 5. 更新记录

```bash
POST /api/kintone/kintone/update_record/

curl -X POST http://127.0.0.1:8000/api/kintone/kintone/update_record/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123",
    "record_id": "1",
    "record_data": {
      "客户名称": {"value": "更新后的客户名"},
      "状态": {"value": "已完成"}
    }
  }'
```

### 6. 批量更新记录

```bash
POST /api/kintone/kintone/update_records/

curl -X POST http://127.0.0.1:8000/api/kintone/kintone/update_records/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123",
    "records_data": [
      {
        "id": "1",
        "record": {
          "状态": {"value": "处理中"}
        }
      },
      {
        "id": "2",
        "record": {
          "状态": {"value": "已完成"}
        }
      }
    ]
  }'
```

### 7. 删除记录

```bash
POST /api/kintone/kintone/delete_records/

curl -X POST http://127.0.0.1:8000/api/kintone/kintone/delete_records/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123",
    "record_ids": ["1", "2", "3"]
  }'
```

### 8. 获取应用信息

```bash
POST /api/kintone/kintone/get_app_info/

curl -X POST http://127.0.0.1:8000/api/kintone/kintone/get_app_info/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123"
  }'
```

### 9. 获取表单字段

```bash
POST /api/kintone/kintone/get_form_fields/

curl -X POST http://127.0.0.1:8000/api/kintone/kintone/get_form_fields/ \
  -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "123"
  }'
```

## Python集成示例

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api/kintone"
AUTH = ("admin", "password")

class KintoneClient:
    def __init__(self, app_id, connection_id=None):
        self.app_id = app_id
        self.connection_id = connection_id
    
    def get_records(self, query=None, fields=None):
        """获取记录列表"""
        url = f"{BASE_URL}/kintone/get_records/"
        data = {
            "app_id": self.app_id,
            "query": query,
            "fields": fields,
            "total_count": True
        }
        if self.connection_id:
            data["connection_id"] = self.connection_id
        
        response = requests.post(url, json=data, auth=AUTH)
        return response.json()
    
    def add_record(self, record_data):
        """添加记录"""
        url = f"{BASE_URL}/kintone/add_record/"
        data = {
            "app_id": self.app_id,
            "record_data": record_data
        }
        if self.connection_id:
            data["connection_id"] = self.connection_id
        
        response = requests.post(url, json=data, auth=AUTH)
        return response.json()
    
    def update_record(self, record_id, record_data):
        """更新记录"""
        url = f"{BASE_URL}/kintone/update_record/"
        data = {
            "app_id": self.app_id,
            "record_id": record_id,
            "record_data": record_data
        }
        if self.connection_id:
            data["connection_id"] = self.connection_id
        
        response = requests.post(url, json=data, auth=AUTH)
        return response.json()
    
    def delete_records(self, record_ids):
        """删除记录"""
        url = f"{BASE_URL}/kintone/delete_records/"
        data = {
            "app_id": self.app_id,
            "record_ids": record_ids
        }
        if self.connection_id:
            data["connection_id"] = self.connection_id
        
        response = requests.post(url, json=data, auth=AUTH)
        return response.json()

# 使用示例
if __name__ == "__main__":
    client = KintoneClient(app_id="123")
    
    # 添加记录
    result = client.add_record({
        "客户名称": {"value": "Python客户"},
        "联系电话": {"value": "1234567890"}
    })
    print(f"添加结果: {result}")
    
    # 获取记录
    records = client.get_records(query='客户名称 = "Python客户"')
    print(f"记录: {records}")
    
    # 更新记录
    if records['data']['records']:
        record_id = records['data']['records'][0]['$id']['value']
        update_result = client.update_record(
            record_id,
            {"状态": {"value": "已确认"}}
        )
        print(f"更新结果: {update_result}")
```

## Kintone查询语法

Kintone使用特殊的查询语法来筛选记录：

```
# 等于
客户名称 = "测试公司"

# 不等于
状态 != "已完成"

# 模糊匹配
客户名称 like "测试"

# 数字比较
金额 > 1000
金额 >= 1000
金额 < 5000
金额 <= 5000

# 日期比较
创建日期 > "2024-01-01"
更新日期 < TODAY()

# 多条件（AND）
客户名称 like "测试" and 状态 = "进行中"

# 多条件（OR）
状态 = "进行中" or 状态 = "待处理"

# IN操作
状态 in ("进行中", "待处理", "已完成")

# 排序
order by 创建日期 desc
order by 金额 asc

# 限制数量
limit 100

# 组合示例
客户名称 like "测试" and 金额 > 1000 order by 创建日期 desc limit 50
```

## Admin后台功能

### 1. Kintone连接管理
- 添加、编辑、删除连接
- 支持密码认证和API Token认证
- 来宾空间配置
- 查看连接状态

### 2. Kintone应用管理
- 管理应用配置
- 查看调用统计
- 启用/禁用应用

### 3. 请求日志
- 详细的API调用记录
- 按操作类型筛选
- 按状态筛选
- 查看请求/响应详情
- 性能分析

### 4. 字段映射
- 配置Kintone字段映射
- 便于系统集成
- 字段类型管理

## 字段数据格式

Kintone的字段数据使用特殊的格式：

```python
# 单行文本
{"value": "文本内容"}

# 数字
{"value": "1000"}

# 日期
{"value": "2024-01-01"}

# 日期时间
{"value": "2024-01-01T12:00:00Z"}

# 单选
{"value": "选项A"}

# 复选框
{"value": ["选项1", "选项2"]}

# 下拉菜单
{"value": "选项A"}

# 用户选择
{"value": [{"code": "user1"}]}

# 表格（子表）
{"value": [
  {
    "value": {
      "子表字段1": {"value": "值1"},
      "子表字段2": {"value": "值2"}
    }
  }
]}
```

## 常见问题

### Q1: API Token无效？
**A:** 
1. 确认Token已生成
2. 确认应用设置已更新
3. 检查Token权限配置
4. Token可能已过期，重新生成

### Q2: 记录添加失败？
**A:**
1. 检查必填字段是否都已提供
2. 验证字段代码是否正确
3. 确认字段值格式正确
4. 查看Admin后台日志了解详细错误

### Q3: 如何获取应用ID？
**A:** 
打开Kintone应用，URL中的数字就是应用ID：
```
https://your-company.cybozu.com/k/123/
                                     ^^^
                                   应用ID
```

### Q4: 查询无结果？
**A:**
1. 检查查询语法是否正确
2. 验证字段代码（区分大小写）
3. 确认数据确实存在
4. 尝试不带query参数获取所有记录

### Q5: 如何使用来宾空间？
**A:**
1. 在连接配置中启用"使用来宾空间"
2. 填写来宾空间ID
3. 确保API Token来自来宾空间应用

## 最佳实践

### 1. 性能优化
- 使用query参数筛选记录，减少数据传输
- 使用fields参数只获取需要的字段
- 批量操作时一次处理多条记录
- 合理使用limit限制返回数量

### 2. 错误处理
```python
try:
    result = client.add_record(record_data)
    if result['status'] == 'success':
        print("成功")
    else:
        print(f"失败: {result['message']}")
except Exception as e:
    print(f"错误: {e}")
```

### 3. 日志监控
- 定期查看Admin后台的请求日志
- 关注失败的请求
- 分析响应时间优化性能

### 4. 安全建议
- 使用API Token而非密码认证
- 定期更新API Token
- 合理设置Token权限
- 不要在代码中硬编码凭证

## API端点列表

### 连接管理
- `GET /api/kintone/connections/` - 列出所有连接
- `POST /api/kintone/connections/` - 创建连接
- `GET /api/kintone/connections/{id}/` - 获取连接详情
- `PUT /api/kintone/connections/{id}/` - 更新连接
- `DELETE /api/kintone/connections/{id}/` - 删除连接

### 应用管理
- `GET /api/kintone/apps/` - 列出所有应用
- `POST /api/kintone/apps/` - 创建应用配置
- `GET /api/kintone/apps/statistics/` - 获取统计信息

### 日志查看
- `GET /api/kintone/logs/` - 列出请求日志
- `GET /api/kintone/logs/statistics/` - 获取使用统计

### Kintone操作
- `POST /api/kintone/kintone/get_records/` - 获取记录列表
- `POST /api/kintone/kintone/get_record/` - 获取单条记录
- `POST /api/kintone/kintone/add_record/` - 添加记录
- `POST /api/kintone/kintone/add_records/` - 批量添加记录
- `POST /api/kintone/kintone/update_record/` - 更新记录
- `POST /api/kintone/kintone/update_records/` - 批量更新记录
- `POST /api/kintone/kintone/delete_records/` - 删除记录
- `POST /api/kintone/kintone/get_app_info/` - 获取应用信息
- `POST /api/kintone/kintone/get_form_fields/` - 获取表单字段

## 下一步

1. 在Admin后台配置Kintone连接
2. 添加应用配置
3. 测试API调用
4. 集成到您的系统

---

**祝使用愉快！** 🚀

如有问题，请查看Admin后台的请求日志了解详细错误信息。

