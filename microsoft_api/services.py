"""
微软API服务类
处理与Microsoft Graph API的交互
"""
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from .models import APIToken, APIUsageLog


class MicrosoftGraphService:
    """Microsoft Graph API基础服务类"""
    
    BASE_URL = "https://graph.microsoft.com/v1.0"
    AUTH_URL = "https://login.microsoftonline.com"
    
    def __init__(self, token_id=None):
        """
        初始化服务
        :param token_id: APIToken的ID，如果为None则使用第一个活跃的token
        """
        if token_id:
            self.api_token = APIToken.objects.get(id=token_id, is_active=True)
        else:
            self.api_token = APIToken.objects.filter(is_active=True).first()
            
        if not self.api_token:
            raise ValueError("没有可用的API Token")
    
    def get_access_token(self):
        """获取访问令牌，如果过期则刷新"""
        if self.api_token.is_token_valid():
            return self.api_token.access_token
        
        # Token过期或不存在，重新获取
        token_url = f"{self.AUTH_URL}/{self.api_token.tenant_id}/oauth2/v2.0/token"
        
        data = {
            'client_id': self.api_token.client_id,
            'client_secret': self.api_token.client_secret,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.api_token.access_token = token_data['access_token']
            # 提前5分钟过期
            expires_in = token_data.get('expires_in', 3600) - 300
            self.api_token.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
            self.api_token.save()
            return self.api_token.access_token
        else:
            raise Exception(f"获取访问令牌失败: {response.text}")
    
    def get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }
    
    def make_request(self, method, endpoint, data=None, params=None, log_endpoint=None, user=None):
        """
        发送API请求
        :param method: HTTP方法
        :param endpoint: API端点路径
        :param data: 请求体数据
        :param params: URL参数
        :param log_endpoint: APIEndpoint对象，用于记录日志
        :param user: 调用用户
        :return: 响应数据
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        headers = self.get_headers()
        
        start_time = datetime.now()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # 记录日志
            if log_endpoint:
                status = 'success' if response.status_code < 400 else 'failed'
                
                APIUsageLog.objects.create(
                    endpoint=log_endpoint,
                    token=self.api_token,
                    request_method=method,
                    request_url=url,
                    request_body=str(data) if data else None,
                    request_headers={'Authorization': 'Bearer ***'},  # 隐藏敏感信息
                    status_code=response.status_code,
                    response_body=response.text[:5000],  # 限制长度
                    response_time=response_time,
                    status=status,
                    error_message=response.text if status == 'failed' else None,
                    user=user
                )
                
                # 更新端点统计
                log_endpoint.total_calls += 1
                log_endpoint.last_called = timezone.now()
                log_endpoint.save()
            
            response.raise_for_status()
            return response.json() if response.content else None
            
        except Exception as e:
            # 记录错误日志
            if log_endpoint:
                APIUsageLog.objects.create(
                    endpoint=log_endpoint,
                    token=self.api_token,
                    request_method=method,
                    request_url=url,
                    request_body=str(data) if data else None,
                    status='error',
                    error_message=str(e),
                    user=user
                )
            raise


class TeamsService(MicrosoftGraphService):
    """Microsoft Teams服务"""
    
    def send_channel_message(self, team_id, channel_id, message, user=None):
        """
        发送频道消息
        :param team_id: 团队ID
        :param channel_id: 频道ID
        :param message: 消息内容
        :param user: 调用用户
        """
        endpoint = f"teams/{team_id}/channels/{channel_id}/messages"
        data = {
            "body": {
                "content": message
            }
        }
        
        from .models import APIEndpoint
        log_endpoint = APIEndpoint.objects.filter(
            service='teams',
            endpoint_url__icontains='messages',
            is_active=True
        ).first()
        
        return self.make_request('POST', endpoint, data=data, log_endpoint=log_endpoint, user=user)
    
    def send_chat_message(self, chat_id, message, user=None):
        """
        发送聊天消息
        :param chat_id: 聊天ID
        :param message: 消息内容
        :param user: 调用用户
        """
        endpoint = f"chats/{chat_id}/messages"
        data = {
            "body": {
                "content": message
            }
        }
        
        from .models import APIEndpoint
        log_endpoint = APIEndpoint.objects.filter(
            service='teams',
            endpoint_url__icontains='chats',
            is_active=True
        ).first()
        
        return self.make_request('POST', endpoint, data=data, log_endpoint=log_endpoint, user=user)
    
    def list_teams(self, user=None):
        """列出所有团队"""
        endpoint = "me/joinedTeams"
        
        from .models import APIEndpoint
        log_endpoint = APIEndpoint.objects.filter(
            service='teams',
            endpoint_url__icontains='joinedTeams',
            is_active=True
        ).first()
        
        return self.make_request('GET', endpoint, log_endpoint=log_endpoint, user=user)


class OutlookService(MicrosoftGraphService):
    """Outlook邮件服务"""
    
    def send_email(self, to_recipients, subject, body, cc_recipients=None, is_html=True, user=None):
        """
        发送邮件
        :param to_recipients: 收件人列表 ['email@example.com']
        :param subject: 邮件主题
        :param body: 邮件正文
        :param cc_recipients: 抄送列表
        :param is_html: 是否HTML格式
        :param user: 调用用户
        """
        endpoint = "me/sendMail"
        
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if is_html else "Text",
                    "content": body
                },
                "toRecipients": [
                    {"emailAddress": {"address": email}} for email in to_recipients
                ]
            }
        }
        
        if cc_recipients:
            message["message"]["ccRecipients"] = [
                {"emailAddress": {"address": email}} for email in cc_recipients
            ]
        
        from .models import APIEndpoint
        log_endpoint = APIEndpoint.objects.filter(
            service='outlook',
            endpoint_url__icontains='sendMail',
            is_active=True
        ).first()
        
        return self.make_request('POST', endpoint, data=message, log_endpoint=log_endpoint, user=user)
    
    def list_messages(self, folder='inbox', top=10, user=None):
        """
        列出邮件
        :param folder: 文件夹名称
        :param top: 获取数量
        :param user: 调用用户
        """
        endpoint = f"me/mailFolders/{folder}/messages"
        params = {'$top': top}
        
        from .models import APIEndpoint
        log_endpoint = APIEndpoint.objects.filter(
            service='outlook',
            endpoint_url__icontains='messages',
            is_active=True
        ).first()
        
        return self.make_request('GET', endpoint, params=params, log_endpoint=log_endpoint, user=user)


class SharePointService(MicrosoftGraphService):
    """SharePoint服务"""
    
    def get_site(self, site_id, user=None):
        """
        获取站点信息
        :param site_id: 站点ID
        :param user: 调用用户
        """
        endpoint = f"sites/{site_id}"
        
        from .models import APIEndpoint
        log_endpoint = APIEndpoint.objects.filter(
            service='sharepoint',
            endpoint_url__icontains='sites',
            is_active=True
        ).first()
        
        return self.make_request('GET', endpoint, log_endpoint=log_endpoint, user=user)
    
    def list_site_lists(self, site_id, user=None):
        """
        获取站点的列表
        :param site_id: 站点ID
        :param user: 调用用户
        """
        endpoint = f"sites/{site_id}/lists"
        
        from .models import APIEndpoint
        log_endpoint = APIEndpoint.objects.filter(
            service='sharepoint',
            endpoint_url__icontains='lists',
            is_active=True
        ).first()
        
        return self.make_request('GET', endpoint, log_endpoint=log_endpoint, user=user)
    
    def get_list_items(self, site_id, list_id, user=None):
        """
        获取列表项
        :param site_id: 站点ID
        :param list_id: 列表ID
        :param user: 调用用户
        """
        endpoint = f"sites/{site_id}/lists/{list_id}/items"
        
        from .models import APIEndpoint
        log_endpoint = APIEndpoint.objects.filter(
            service='sharepoint',
            endpoint_url__icontains='items',
            is_active=True
        ).first()
        
        return self.make_request('GET', endpoint, log_endpoint=log_endpoint, user=user)
    
    def upload_file(self, site_id, drive_id, file_path, file_content, user=None):
        """
        上传文件到SharePoint
        :param site_id: 站点ID
        :param drive_id: 驱动器ID
        :param file_path: 文件路径
        :param file_content: 文件内容
        :param user: 调用用户
        """
        endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{file_path}:/content"
        
        # 特殊处理：文件上传需要不同的Content-Type
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/octet-stream'
        }
        
        response = requests.put(url, headers=headers, data=file_content)
        
        from .models import APIEndpoint
        log_endpoint = APIEndpoint.objects.filter(
            service='sharepoint',
            endpoint_url__icontains='upload',
            is_active=True
        ).first()
        
        if log_endpoint:
            log_endpoint.total_calls += 1
            log_endpoint.last_called = timezone.now()
            log_endpoint.save()
            
            APIUsageLog.objects.create(
                endpoint=log_endpoint,
                token=self.api_token,
                request_method='PUT',
                request_url=url,
                status_code=response.status_code,
                response_body=response.text[:5000],
                status='success' if response.status_code < 400 else 'failed',
                user=user
            )
        
        response.raise_for_status()
        return response.json() if response.content else None

