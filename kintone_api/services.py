"""
Kintone API服务类
处理与Kintone API的交互
"""
import requests
import base64
from datetime import datetime
from django.utils import timezone
from .models import KintoneConnection, KintoneApp, KintoneRequestLog


class KintoneService:
    """Kintone API服务基础类"""
    
    def __init__(self, connection_id=None):
        """
        初始化服务
        :param connection_id: KintoneConnection的ID，如果为None则使用第一个活跃的连接
        """
        if connection_id:
            self.connection = KintoneConnection.objects.get(id=connection_id, is_active=True)
        else:
            self.connection = KintoneConnection.objects.filter(is_active=True).first()
        
        if not self.connection:
            raise ValueError("没有可用的Kintone连接")
    
    def get_headers(self):
        """获取请求头"""
        headers = {
            'Content-Type': 'application/json',
        }
        
        if self.connection.auth_type == 'api_token':
            # API Token认证
            headers['X-Cybozu-API-Token'] = self.connection.api_token
        else:
            # 密码认证（Basic Auth）
            credentials = f"{self.connection.username}:{self.connection.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers['X-Cybozu-Authorization'] = encoded
        
        return headers
    
    def build_url(self, endpoint, app_id=None, guest_space_id=None):
        """
        构建API URL
        :param endpoint: API端点，例如 'records.json'
        :param app_id: 应用ID
        :param guest_space_id: 来宾空间ID（可选）
        """
        base_url = self.connection.base_url
        
        # 使用来宾空间
        if guest_space_id or (self.connection.use_guest_space and self.connection.guest_space_id):
            space_id = guest_space_id or self.connection.guest_space_id
            url = f"{base_url}/k/guest/{space_id}/v1/{endpoint}"
        else:
            url = f"{base_url}/k/v1/{endpoint}"
        
        return url
    
    def make_request(self, method, endpoint, app_id=None, params=None, data=None, 
                    action='other', app_obj=None, user=None):
        """
        发送API请求
        :param method: HTTP方法
        :param endpoint: API端点
        :param app_id: 应用ID
        :param params: URL参数
        :param data: 请求体数据
        :param action: 操作类型（用于日志）
        :param app_obj: KintoneApp对象
        :param user: 调用用户
        :return: 响应数据
        """
        url = self.build_url(endpoint, app_id)
        headers = self.get_headers()
        
        start_time = datetime.now()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # 记录日志
            status = 'success' if response.status_code < 400 else 'failed'
            
            KintoneRequestLog.objects.create(
                connection=self.connection,
                app=app_obj,
                action=action,
                request_url=url,
                request_method=method,
                request_params=params,
                request_body=str(data) if data else None,
                status_code=response.status_code,
                response_body=response.text[:5000],  # 限制长度
                response_time=response_time,
                status=status,
                error_message=response.text if status == 'failed' else None,
                user=user
            )
            
            # 更新应用统计
            if app_obj:
                app_obj.total_requests += 1
                app_obj.last_accessed = timezone.now()
                app_obj.save()
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except Exception as e:
            # 记录错误日志
            KintoneRequestLog.objects.create(
                connection=self.connection,
                app=app_obj,
                action=action,
                request_url=url,
                request_method=method,
                request_params=params,
                request_body=str(data) if data else None,
                status='error',
                error_message=str(e),
                user=user
            )
            raise
    
    def get_records(self, app_id, query=None, fields=None, total_count=False, user=None):
        """
        获取记录列表
        :param app_id: 应用ID
        :param query: 查询条件（Kintone查询语法）
        :param fields: 要获取的字段列表
        :param total_count: 是否获取总数
        :param user: 调用用户
        """
        params = {'app': app_id}
        
        if query:
            params['query'] = query
        if fields:
            params['fields'] = fields
        if total_count:
            params['totalCount'] = 'true'
        
        app_obj = KintoneApp.objects.filter(
            connection=self.connection, 
            app_id=app_id
        ).first()
        
        return self.make_request(
            'GET', 
            'records.json', 
            app_id=app_id,
            params=params,
            action='get_records',
            app_obj=app_obj,
            user=user
        )
    
    def get_record(self, app_id, record_id, user=None):
        """
        获取单条记录
        :param app_id: 应用ID
        :param record_id: 记录ID
        :param user: 调用用户
        """
        params = {
            'app': app_id,
            'id': record_id
        }
        
        app_obj = KintoneApp.objects.filter(
            connection=self.connection, 
            app_id=app_id
        ).first()
        
        return self.make_request(
            'GET',
            'record.json',
            app_id=app_id,
            params=params,
            action='get_record',
            app_obj=app_obj,
            user=user
        )
    
    def add_record(self, app_id, record_data, user=None):
        """
        添加记录
        :param app_id: 应用ID
        :param record_data: 记录数据（字典格式）
        :param user: 调用用户
        """
        data = {
            'app': app_id,
            'record': record_data
        }
        
        app_obj = KintoneApp.objects.filter(
            connection=self.connection, 
            app_id=app_id
        ).first()
        
        return self.make_request(
            'POST',
            'record.json',
            app_id=app_id,
            data=data,
            action='add_record',
            app_obj=app_obj,
            user=user
        )
    
    def add_records(self, app_id, records_data, user=None):
        """
        批量添加记录
        :param app_id: 应用ID
        :param records_data: 记录数据列表
        :param user: 调用用户
        """
        data = {
            'app': app_id,
            'records': records_data
        }
        
        app_obj = KintoneApp.objects.filter(
            connection=self.connection, 
            app_id=app_id
        ).first()
        
        return self.make_request(
            'POST',
            'records.json',
            app_id=app_id,
            data=data,
            action='add_record',
            app_obj=app_obj,
            user=user
        )
    
    def update_record(self, app_id, record_id, record_data, revision=None, user=None):
        """
        更新记录
        :param app_id: 应用ID
        :param record_id: 记录ID
        :param record_data: 要更新的字段数据
        :param revision: 修订号（用于乐观锁）
        :param user: 调用用户
        """
        data = {
            'app': app_id,
            'id': record_id,
            'record': record_data
        }
        
        if revision:
            data['revision'] = revision
        
        app_obj = KintoneApp.objects.filter(
            connection=self.connection, 
            app_id=app_id
        ).first()
        
        return self.make_request(
            'PUT',
            'record.json',
            app_id=app_id,
            data=data,
            action='update_record',
            app_obj=app_obj,
            user=user
        )
    
    def update_records(self, app_id, records_data, user=None):
        """
        批量更新记录
        :param app_id: 应用ID
        :param records_data: 记录数据列表，每个包含id和record
        :param user: 调用用户
        """
        data = {
            'app': app_id,
            'records': records_data
        }
        
        app_obj = KintoneApp.objects.filter(
            connection=self.connection, 
            app_id=app_id
        ).first()
        
        return self.make_request(
            'PUT',
            'records.json',
            app_id=app_id,
            data=data,
            action='update_record',
            app_obj=app_obj,
            user=user
        )
    
    def delete_records(self, app_id, record_ids, user=None):
        """
        删除记录
        :param app_id: 应用ID
        :param record_ids: 记录ID列表
        :param user: 调用用户
        """
        data = {
            'app': app_id,
            'ids': record_ids
        }
        
        app_obj = KintoneApp.objects.filter(
            connection=self.connection, 
            app_id=app_id
        ).first()
        
        return self.make_request(
            'DELETE',
            'records.json',
            app_id=app_id,
            data=data,
            action='delete_records',
            app_obj=app_obj,
            user=user
        )
    
    def get_app_info(self, app_id, user=None):
        """
        获取应用信息
        :param app_id: 应用ID
        :param user: 调用用户
        """
        params = {'id': app_id}
        
        app_obj = KintoneApp.objects.filter(
            connection=self.connection, 
            app_id=app_id
        ).first()
        
        return self.make_request(
            'GET',
            'app.json',
            app_id=app_id,
            params=params,
            action='get_app_info',
            app_obj=app_obj,
            user=user
        )
    
    def get_form_fields(self, app_id, user=None):
        """
        获取表单字段配置
        :param app_id: 应用ID
        :param user: 调用用户
        """
        params = {'app': app_id}
        
        app_obj = KintoneApp.objects.filter(
            connection=self.connection, 
            app_id=app_id
        ).first()
        
        return self.make_request(
            'GET',
            'app/form/fields.json',
            app_id=app_id,
            params=params,
            action='get_form_fields',
            app_obj=app_obj,
            user=user
        )
    
    def upload_file(self, file_data, file_name, user=None):
        """
        上传文件到Kintone
        :param file_data: 文件二进制数据
        :param file_name: 文件名
        :param user: 调用用户
        """
        url = self.build_url('file.json')
        headers = self.get_headers()
        # 文件上传需要multipart/form-data
        headers.pop('Content-Type', None)
        
        files = {'file': (file_name, file_data)}
        
        start_time = datetime.now()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                files=files
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            status = 'success' if response.status_code < 400 else 'failed'
            
            KintoneRequestLog.objects.create(
                connection=self.connection,
                action='upload_file',
                request_url=url,
                request_method='POST',
                status_code=response.status_code,
                response_body=response.text[:5000],
                response_time=response_time,
                status=status,
                user=user
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            KintoneRequestLog.objects.create(
                connection=self.connection,
                action='upload_file',
                request_url=url,
                request_method='POST',
                status='error',
                error_message=str(e),
                user=user
            )
            raise

