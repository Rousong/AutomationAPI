"""
Kintone Admin后台配置
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import KintoneConnection, KintoneApp, KintoneRequestLog, KintoneFieldMapping


@admin.register(KintoneConnection)
class KintoneConnectionAdmin(admin.ModelAdmin):
    """Kintone连接管理"""
    
    list_display = ['name', 'subdomain', 'auth_type', 'is_active', 'created_at']
    list_filter = ['auth_type', 'is_active', 'use_guest_space', 'created_at']
    search_fields = ['name', 'subdomain', 'username']
    readonly_fields = ['base_url', 'created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'subdomain', 'is_active')
        }),
        ('认证配置', {
            'fields': ('auth_type', 'username', 'password', 'api_token'),
            'description': '根据认证方式选择填写：密码认证填写用户名和密码，API Token认证填写API Token'
        }),
        ('来宾空间配置', {
            'fields': ('use_guest_space', 'guest_space_id'),
            'classes': ('collapse',)
        }),
        ('系统信息', {
            'fields': ('base_url', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(KintoneApp)
class KintoneAppAdmin(admin.ModelAdmin):
    """Kintone应用管理"""
    
    list_display = ['app_name', 'app_id', 'connection', 'is_active', 
                   'total_requests', 'last_accessed']
    list_filter = ['connection', 'is_active', 'created_at']
    search_fields = ['app_name', 'app_id', 'description']
    readonly_fields = ['total_requests', 'last_accessed', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('connection', 'app_id', 'app_name', 'is_active')
        }),
        ('应用描述', {
            'fields': ('description',)
        }),
        ('统计信息', {
            'fields': ('total_requests', 'last_accessed'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(KintoneRequestLog)
class KintoneRequestLogAdmin(admin.ModelAdmin):
    """Kintone请求日志管理"""
    
    list_display = ['app', 'action_badge', 'status_badge', 'request_method', 
                   'status_code', 'response_time', 'user', 'created_at']
    list_filter = ['status', 'action', 'request_method', 'created_at']
    search_fields = ['request_url', 'error_message', 'app__app_name']
    readonly_fields = ['connection', 'app', 'action', 'request_url', 
                      'request_method', 'request_params', 'request_body',
                      'status_code', 'response_body', 'response_time',
                      'status', 'error_message', 'user', 'created_at']
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('connection', 'app', 'action', 'status', 'user', 'created_at')
        }),
        ('请求信息', {
            'fields': ('request_method', 'request_url', 'request_params', 'request_body')
        }),
        ('响应信息', {
            'fields': ('status_code', 'response_body', 'response_time')
        }),
        ('错误信息', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def action_badge(self, obj):
        """操作类型徽章"""
        colors = {
            'get_records': 'blue',
            'get_record': 'blue',
            'add_record': 'green',
            'update_record': 'orange',
            'delete_records': 'red',
            'get_app_info': 'purple',
            'get_form_fields': 'purple',
        }
        color = colors.get(obj.action, 'gray')
        return format_html(
            '<span style="color: {};">● {}</span>',
            color, obj.get_action_display()
        )
    action_badge.short_description = '操作'
    
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


@admin.register(KintoneFieldMapping)
class KintoneFieldMappingAdmin(admin.ModelAdmin):
    """Kintone字段映射管理"""
    
    list_display = ['field_name', 'field_code', 'field_type', 'app', 
                   'external_field_name', 'is_required']
    list_filter = ['app', 'field_type', 'is_required']
    search_fields = ['field_code', 'field_name', 'field_type', 'external_field_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Kintone字段信息', {
            'fields': ('app', 'field_code', 'field_name', 'field_type', 'is_required')
        }),
        ('映射配置', {
            'fields': ('external_field_name', 'description')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 更新Admin站点标题
admin.site.site_header = 'AutomationAPI 管理后台'
admin.site.site_title = 'AutomationAPI'
admin.site.index_title = '微软API & Kintone API 自动化管理系统'
