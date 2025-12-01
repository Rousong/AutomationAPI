"""
Kintone API序列化器
"""
from rest_framework import serializers
from .models import KintoneConnection, KintoneApp, KintoneRequestLog, KintoneFieldMapping


class KintoneConnectionSerializer(serializers.ModelSerializer):
    """Kintone连接序列化器"""
    
    base_url = serializers.ReadOnlyField()
    
    class Meta:
        model = KintoneConnection
        fields = [
            'id', 'name', 'subdomain', 'auth_type', 'username', 'password',
            'api_token', 'is_active', 'use_guest_space', 'guest_space_id',
            'base_url', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'api_token': {'write_only': True},
        }


class KintoneConnectionListSerializer(serializers.ModelSerializer):
    """Kintone连接列表序列化器（隐藏敏感信息）"""
    
    auth_type_display = serializers.CharField(source='get_auth_type_display', read_only=True)
    
    class Meta:
        model = KintoneConnection
        fields = ['id', 'name', 'subdomain', 'auth_type', 'auth_type_display', 
                 'is_active', 'created_at']


class KintoneAppSerializer(serializers.ModelSerializer):
    """Kintone应用序列化器"""
    
    connection_name = serializers.CharField(source='connection.name', read_only=True)
    
    class Meta:
        model = KintoneApp
        fields = [
            'id', 'connection', 'connection_name', 'app_id', 'app_name',
            'description', 'total_requests', 'last_accessed', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_requests', 'last_accessed']


class KintoneRequestLogSerializer(serializers.ModelSerializer):
    """Kintone请求日志序列化器"""
    
    connection_name = serializers.CharField(source='connection.name', read_only=True)
    app_name = serializers.CharField(source='app.app_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = KintoneRequestLog
        fields = [
            'id', 'connection', 'connection_name', 'app', 'app_name',
            'action', 'action_display', 'request_method', 'request_url',
            'status_code', 'response_time', 'status', 'status_display',
            'error_message', 'user', 'username', 'created_at'
        ]


class KintoneRequestLogDetailSerializer(serializers.ModelSerializer):
    """Kintone请求日志详细序列化器"""
    
    connection_name = serializers.CharField(source='connection.name', read_only=True)
    app_name = serializers.CharField(source='app.app_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = KintoneRequestLog
        fields = '__all__'


class KintoneFieldMappingSerializer(serializers.ModelSerializer):
    """Kintone字段映射序列化器"""
    
    app_name = serializers.CharField(source='app.app_name', read_only=True)
    
    class Meta:
        model = KintoneFieldMapping
        fields = '__all__'


# 操作序列化器

class KintoneGetRecordsSerializer(serializers.Serializer):
    """获取记录列表"""
    
    connection_id = serializers.IntegerField(required=False, help_text='连接ID，不提供则使用默认')
    app_id = serializers.CharField(help_text='应用ID')
    query = serializers.CharField(required=False, allow_blank=True, 
                                  help_text='查询条件（Kintone查询语法）')
    fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='要获取的字段列表'
    )
    total_count = serializers.BooleanField(default=False, help_text='是否获取总数')


class KintoneGetRecordSerializer(serializers.Serializer):
    """获取单条记录"""
    
    connection_id = serializers.IntegerField(required=False, help_text='连接ID')
    app_id = serializers.CharField(help_text='应用ID')
    record_id = serializers.CharField(help_text='记录ID')


class KintoneAddRecordSerializer(serializers.Serializer):
    """添加记录"""
    
    connection_id = serializers.IntegerField(required=False, help_text='连接ID')
    app_id = serializers.CharField(help_text='应用ID')
    record_data = serializers.JSONField(help_text='记录数据（字典格式）')


class KintoneAddRecordsSerializer(serializers.Serializer):
    """批量添加记录"""
    
    connection_id = serializers.IntegerField(required=False, help_text='连接ID')
    app_id = serializers.CharField(help_text='应用ID')
    records_data = serializers.ListField(
        child=serializers.JSONField(),
        help_text='记录数据列表'
    )


class KintoneUpdateRecordSerializer(serializers.Serializer):
    """更新记录"""
    
    connection_id = serializers.IntegerField(required=False, help_text='连接ID')
    app_id = serializers.CharField(help_text='应用ID')
    record_id = serializers.CharField(help_text='记录ID')
    record_data = serializers.JSONField(help_text='要更新的字段数据')
    revision = serializers.IntegerField(required=False, help_text='修订号（用于乐观锁）')


class KintoneUpdateRecordsSerializer(serializers.Serializer):
    """批量更新记录"""
    
    connection_id = serializers.IntegerField(required=False, help_text='连接ID')
    app_id = serializers.CharField(help_text='应用ID')
    records_data = serializers.ListField(
        child=serializers.JSONField(),
        help_text='记录数据列表，每个包含id和record'
    )


class KintoneDeleteRecordsSerializer(serializers.Serializer):
    """删除记录"""
    
    connection_id = serializers.IntegerField(required=False, help_text='连接ID')
    app_id = serializers.CharField(help_text='应用ID')
    record_ids = serializers.ListField(
        child=serializers.CharField(),
        help_text='记录ID列表'
    )


class KintoneGetAppInfoSerializer(serializers.Serializer):
    """获取应用信息"""
    
    connection_id = serializers.IntegerField(required=False, help_text='连接ID')
    app_id = serializers.CharField(help_text='应用ID')


class KintoneGetFormFieldsSerializer(serializers.Serializer):
    """获取表单字段"""
    
    connection_id = serializers.IntegerField(required=False, help_text='连接ID')
    app_id = serializers.CharField(help_text='应用ID')

