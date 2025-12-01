"""
Admin后台配置
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import APIToken, APIEndpoint, APIUsageLog, TeamsMessage, EmailTemplate


@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    """API Token管理"""
    
    list_display = ['name', 'is_active', 'token_status', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'client_id', 'tenant_id']
    readonly_fields = ['access_token', 'token_expires_at', 'created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'is_active')
        }),
        ('认证信息', {
            'fields': ('client_id', 'client_secret', 'tenant_id')
        }),
        ('Token缓存（系统管理）', {
            'fields': ('access_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def token_status(self, obj):
        """Token状态"""
        if obj.is_token_valid():
            return format_html('<span style="color: green;">✓ 有效</span>')
        return format_html('<span style="color: red;">✗ 无效/过期</span>')
    token_status.short_description = 'Token状态'
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(APIEndpoint)
class APIEndpointAdmin(admin.ModelAdmin):
    """API端点管理"""
    
    list_display = ['name', 'service', 'http_method', 'is_active', 'total_calls', 'last_called']
    list_filter = ['service', 'http_method', 'is_active']
    search_fields = ['name', 'endpoint_url', 'description']
    readonly_fields = ['total_calls', 'last_called', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'service', 'is_active')
        }),
        ('端点配置', {
            'fields': ('endpoint_url', 'http_method', 'requires_body', 'description')
        }),
        ('统计信息', {
            'fields': ('total_calls', 'last_called'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    """API使用日志管理"""
    
    list_display = ['endpoint', 'status_badge', 'request_method', 'status_code', 
                   'response_time', 'user', 'created_at']
    list_filter = ['status', 'request_method', 'endpoint__service', 'created_at']
    search_fields = ['endpoint__name', 'request_url', 'error_message']
    readonly_fields = ['endpoint', 'token', 'request_method', 'request_url', 
                      'request_body', 'request_headers', 'status_code', 
                      'response_body', 'response_time', 'status', 
                      'error_message', 'user', 'created_at']
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('endpoint', 'token', 'user', 'status', 'created_at')
        }),
        ('请求信息', {
            'fields': ('request_method', 'request_url', 'request_body', 'request_headers')
        }),
        ('响应信息', {
            'fields': ('status_code', 'response_body', 'response_time')
        }),
        ('错误信息', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """状态徽章"""
        colors = {
            'success': 'green',
            'failed': 'orange',
            'error': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">● {}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def has_add_permission(self, request):
        """禁止手动添加日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改日志"""
        return False


@admin.register(TeamsMessage)
class TeamsMessageAdmin(admin.ModelAdmin):
    """Teams消息模板管理"""
    
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'message_template']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'is_active')
        }),
        ('目标配置', {
            'fields': ('team_id', 'channel_id', 'chat_id'),
            'description': '配置消息发送的目标，频道消息需要team_id和channel_id，聊天消息需要chat_id'
        }),
        ('消息内容', {
            'fields': ('message_template',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """邮件模板管理"""
    
    list_display = ['name', 'subject', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'subject', 'body_template']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'is_active')
        }),
        ('邮件配置', {
            'fields': ('subject', 'body_template')
        }),
        ('默认收件人', {
            'fields': ('default_recipients', 'default_cc'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 自定义Admin站点配置
admin.site.site_header = 'AutomationAPI 管理后台'
admin.site.site_title = 'AutomationAPI'
admin.site.index_title = '微软API自动化管理系统'
