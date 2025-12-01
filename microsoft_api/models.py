from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class APIToken(models.Model):
    """存储微软API的认证令牌和密钥"""
    
    name = models.CharField(max_length=100, verbose_name='Token名称', help_text='用于识别此Token的名称')
    client_id = models.CharField(max_length=255, verbose_name='Client ID')
    client_secret = models.CharField(max_length=255, verbose_name='Client Secret')
    tenant_id = models.CharField(max_length=255, verbose_name='Tenant ID')
    
    # 访问令牌缓存
    access_token = models.TextField(blank=True, null=True, verbose_name='Access Token')
    token_expires_at = models.DateTimeField(blank=True, null=True, verbose_name='Token过期时间')
    
    # 配置信息
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建者')
    
    class Meta:
        verbose_name = 'API Token'
        verbose_name_plural = 'API Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({'活跃' if self.is_active else '禁用'})"
    
    def is_token_valid(self):
        """检查Token是否有效"""
        if not self.access_token or not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at


class APIEndpoint(models.Model):
    """管理不同的API端点配置"""
    
    SERVICE_CHOICES = [
        ('teams', 'Microsoft Teams'),
        ('outlook', 'Outlook'),
        ('sharepoint', 'SharePoint'),
        ('graph', 'Microsoft Graph (通用)'),
    ]
    
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='端点名称')
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, verbose_name='服务类型')
    endpoint_url = models.CharField(max_length=500, verbose_name='端点URL', 
                                    help_text='相对于 https://graph.microsoft.com/v1.0/ 的路径')
    http_method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='GET', verbose_name='HTTP方法')
    description = models.TextField(blank=True, verbose_name='描述')
    
    # 配置
    requires_body = models.BooleanField(default=False, verbose_name='需要请求体')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 统计
    total_calls = models.IntegerField(default=0, verbose_name='总调用次数')
    last_called = models.DateTimeField(blank=True, null=True, verbose_name='最后调用时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'API端点'
        verbose_name_plural = 'API端点'
        ordering = ['service', 'name']
    
    def __str__(self):
        return f"{self.get_service_display()} - {self.name}"


class APIUsageLog(models.Model):
    """记录API调用历史和使用情况"""
    
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('error', '错误'),
    ]
    
    endpoint = models.ForeignKey(APIEndpoint, on_delete=models.CASCADE, related_name='usage_logs', 
                                verbose_name='API端点')
    token = models.ForeignKey(APIToken, on_delete=models.SET_NULL, null=True, blank=True, 
                             verbose_name='使用的Token')
    
    # 请求信息
    request_method = models.CharField(max_length=10, verbose_name='请求方法')
    request_url = models.TextField(verbose_name='请求URL')
    request_body = models.TextField(blank=True, null=True, verbose_name='请求体')
    request_headers = models.JSONField(blank=True, null=True, verbose_name='请求头')
    
    # 响应信息
    status_code = models.IntegerField(blank=True, null=True, verbose_name='状态码')
    response_body = models.TextField(blank=True, null=True, verbose_name='响应体')
    response_time = models.FloatField(blank=True, null=True, verbose_name='响应时间(秒)')
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='状态')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    
    # 用户和时间
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='调用用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='调用时间', db_index=True)
    
    class Meta:
        verbose_name = 'API使用日志'
        verbose_name_plural = 'API使用日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['endpoint', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.endpoint.name} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"


class TeamsMessage(models.Model):
    """Teams消息模板"""
    
    name = models.CharField(max_length=100, verbose_name='模板名称')
    channel_id = models.CharField(max_length=255, blank=True, verbose_name='频道ID')
    team_id = models.CharField(max_length=255, blank=True, verbose_name='团队ID')
    chat_id = models.CharField(max_length=255, blank=True, verbose_name='聊天ID')
    
    # 消息内容
    message_template = models.TextField(verbose_name='消息模板', 
                                       help_text='支持变量，如 {user_name}, {message}')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'Teams消息模板'
        verbose_name_plural = 'Teams消息模板'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class EmailTemplate(models.Model):
    """Outlook邮件模板"""
    
    name = models.CharField(max_length=100, verbose_name='模板名称')
    subject = models.CharField(max_length=255, verbose_name='邮件主题')
    body_template = models.TextField(verbose_name='邮件正文模板', 
                                    help_text='支持HTML和变量')
    
    # 默认收件人
    default_recipients = models.TextField(blank=True, verbose_name='默认收件人', 
                                         help_text='多个邮箱用逗号分隔')
    default_cc = models.TextField(blank=True, verbose_name='默认抄送', 
                                 help_text='多个邮箱用逗号分隔')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '邮件模板'
        verbose_name_plural = '邮件模板'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
