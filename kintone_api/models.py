from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class KintoneConnection(models.Model):
    """Kintone连接配置"""
    
    name = models.CharField(max_length=100, verbose_name='连接名称', help_text='用于识别此Kintone连接')
    subdomain = models.CharField(max_length=100, verbose_name='子域名', 
                                 help_text='例如：your-company（不含.cybozu.com）')
    
    # 认证方式
    AUTH_TYPE_CHOICES = [
        ('password', '密码认证'),
        ('api_token', 'API Token认证'),
    ]
    auth_type = models.CharField(max_length=20, choices=AUTH_TYPE_CHOICES, 
                                 default='api_token', verbose_name='认证方式')
    
    # 密码认证字段
    username = models.CharField(max_length=100, blank=True, verbose_name='用户名',
                               help_text='密码认证时使用')
    password = models.CharField(max_length=255, blank=True, verbose_name='密码',
                               help_text='密码认证时使用')
    
    # API Token认证字段
    api_token = models.CharField(max_length=255, blank=True, verbose_name='API Token',
                                 help_text='API Token认证时使用')
    
    # 配置
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    use_guest_space = models.BooleanField(default=False, verbose_name='使用来宾空间')
    guest_space_id = models.CharField(max_length=20, blank=True, verbose_name='来宾空间ID')
    
    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  blank=True, verbose_name='创建者')
    
    class Meta:
        verbose_name = 'Kintone连接'
        verbose_name_plural = 'Kintone连接'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.subdomain}) - {'活跃' if self.is_active else '禁用'}"
    
    @property
    def base_url(self):
        """获取基础URL"""
        return f"https://{self.subdomain}.cybozu.com"


class KintoneApp(models.Model):
    """Kintone应用配置"""
    
    connection = models.ForeignKey(KintoneConnection, on_delete=models.CASCADE, 
                                  related_name='apps', verbose_name='连接')
    app_id = models.CharField(max_length=20, verbose_name='应用ID')
    app_name = models.CharField(max_length=200, verbose_name='应用名称')
    description = models.TextField(blank=True, verbose_name='描述')
    
    # 统计
    total_requests = models.IntegerField(default=0, verbose_name='总请求次数')
    last_accessed = models.DateTimeField(blank=True, null=True, verbose_name='最后访问时间')
    
    # 配置
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'Kintone应用'
        verbose_name_plural = 'Kintone应用'
        ordering = ['connection', 'app_name']
        unique_together = ['connection', 'app_id']
    
    def __str__(self):
        return f"{self.app_name} (ID: {self.app_id})"


class KintoneRequestLog(models.Model):
    """Kintone API请求日志"""
    
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('error', '错误'),
    ]
    
    ACTION_CHOICES = [
        ('get_records', '获取记录'),
        ('get_record', '获取单条记录'),
        ('add_record', '添加记录'),
        ('update_record', '更新记录'),
        ('delete_records', '删除记录'),
        ('get_app_info', '获取应用信息'),
        ('get_form_fields', '获取表单字段'),
        ('upload_file', '上传文件'),
        ('download_file', '下载文件'),
        ('other', '其他'),
    ]
    
    connection = models.ForeignKey(KintoneConnection, on_delete=models.SET_NULL, 
                                  null=True, blank=True, verbose_name='连接')
    app = models.ForeignKey(KintoneApp, on_delete=models.SET_NULL, null=True, 
                           blank=True, related_name='logs', verbose_name='应用')
    
    # 请求信息
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name='操作类型')
    request_url = models.TextField(verbose_name='请求URL')
    request_method = models.CharField(max_length=10, verbose_name='请求方法')
    request_params = models.JSONField(blank=True, null=True, verbose_name='请求参数')
    request_body = models.TextField(blank=True, null=True, verbose_name='请求体')
    
    # 响应信息
    status_code = models.IntegerField(blank=True, null=True, verbose_name='状态码')
    response_body = models.TextField(blank=True, null=True, verbose_name='响应体')
    response_time = models.FloatField(blank=True, null=True, verbose_name='响应时间(秒)')
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='状态')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    
    # 用户和时间
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                            blank=True, verbose_name='调用用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='调用时间', db_index=True)
    
    class Meta:
        verbose_name = 'Kintone请求日志'
        verbose_name_plural = 'Kintone请求日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        app_name = self.app.app_name if self.app else 'N/A'
        return f"{app_name} - {self.get_action_display()} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"


class KintoneFieldMapping(models.Model):
    """Kintone字段映射配置"""
    
    app = models.ForeignKey(KintoneApp, on_delete=models.CASCADE, 
                           related_name='field_mappings', verbose_name='应用')
    field_code = models.CharField(max_length=100, verbose_name='字段代码')
    field_name = models.CharField(max_length=200, verbose_name='字段名称')
    field_type = models.CharField(max_length=50, verbose_name='字段类型',
                                 help_text='例如：SINGLE_LINE_TEXT, NUMBER, DATE等')
    
    # 映射到外部系统的字段名
    external_field_name = models.CharField(max_length=200, blank=True, 
                                          verbose_name='外部字段名',
                                          help_text='映射到其他系统的字段名')
    
    is_required = models.BooleanField(default=False, verbose_name='是否必填')
    description = models.TextField(blank=True, verbose_name='描述')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'Kintone字段映射'
        verbose_name_plural = 'Kintone字段映射'
        ordering = ['app', 'field_code']
        unique_together = ['app', 'field_code']
    
    def __str__(self):
        return f"{self.app.app_name} - {self.field_name} ({self.field_code})"
