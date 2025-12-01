"""
REST API序列化器
"""
from rest_framework import serializers
from .models import APIToken, APIEndpoint, APIUsageLog, TeamsMessage, EmailTemplate


class APITokenSerializer(serializers.ModelSerializer):
    """API Token序列化器"""
    
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = APIToken
        fields = [
            'id', 'name', 'client_id', 'client_secret', 'tenant_id',
            'is_active', 'is_valid', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'client_secret': {'write_only': True},  # 不在响应中返回密钥
        }
    
    def get_is_valid(self, obj):
        """检查Token是否有效"""
        return obj.is_token_valid()


class APITokenListSerializer(serializers.ModelSerializer):
    """API Token列表序列化器（隐藏敏感信息）"""
    
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = APIToken
        fields = ['id', 'name', 'is_active', 'is_valid', 'created_at']
    
    def get_is_valid(self, obj):
        return obj.is_token_valid()


class APIEndpointSerializer(serializers.ModelSerializer):
    """API端点序列化器"""
    
    service_display = serializers.CharField(source='get_service_display', read_only=True)
    
    class Meta:
        model = APIEndpoint
        fields = [
            'id', 'name', 'service', 'service_display', 'endpoint_url',
            'http_method', 'description', 'requires_body', 'is_active',
            'total_calls', 'last_called', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_calls', 'last_called']


class APIUsageLogSerializer(serializers.ModelSerializer):
    """API使用日志序列化器"""
    
    endpoint_name = serializers.CharField(source='endpoint.name', read_only=True)
    token_name = serializers.CharField(source='token.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = APIUsageLog
        fields = [
            'id', 'endpoint', 'endpoint_name', 'token', 'token_name',
            'request_method', 'request_url', 'status_code',
            'response_time', 'status', 'status_display', 'error_message',
            'user', 'username', 'created_at'
        ]


class APIUsageLogDetailSerializer(serializers.ModelSerializer):
    """API使用日志详细序列化器"""
    
    endpoint_name = serializers.CharField(source='endpoint.name', read_only=True)
    token_name = serializers.CharField(source='token.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = APIUsageLog
        fields = '__all__'


class TeamsMessageSerializer(serializers.ModelSerializer):
    """Teams消息模板序列化器"""
    
    class Meta:
        model = TeamsMessage
        fields = '__all__'


class EmailTemplateSerializer(serializers.ModelSerializer):
    """邮件模板序列化器"""
    
    class Meta:
        model = EmailTemplate
        fields = '__all__'


# 操作序列化器（用于API调用）

class SendTeamsMessageSerializer(serializers.Serializer):
    """发送Teams消息"""
    
    MESSAGE_TYPE_CHOICES = [
        ('channel', '频道消息'),
        ('chat', '聊天消息'),
    ]
    
    token_id = serializers.IntegerField(required=False, help_text='API Token ID，不提供则使用默认')
    message_type = serializers.ChoiceField(choices=MESSAGE_TYPE_CHOICES, default='channel')
    team_id = serializers.CharField(required=False, help_text='团队ID（频道消息必需）')
    channel_id = serializers.CharField(required=False, help_text='频道ID（频道消息必需）')
    chat_id = serializers.CharField(required=False, help_text='聊天ID（聊天消息必需）')
    message = serializers.CharField(help_text='消息内容')
    
    def validate(self, data):
        if data['message_type'] == 'channel':
            if not data.get('team_id') or not data.get('channel_id'):
                raise serializers.ValidationError("频道消息需要提供team_id和channel_id")
        elif data['message_type'] == 'chat':
            if not data.get('chat_id'):
                raise serializers.ValidationError("聊天消息需要提供chat_id")
        return data


class SendEmailSerializer(serializers.Serializer):
    """发送邮件"""
    
    token_id = serializers.IntegerField(required=False, help_text='API Token ID，不提供则使用默认')
    to_recipients = serializers.ListField(
        child=serializers.EmailField(),
        help_text='收件人邮箱列表'
    )
    cc_recipients = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        help_text='抄送邮箱列表'
    )
    subject = serializers.CharField(help_text='邮件主题')
    body = serializers.CharField(help_text='邮件正文')
    is_html = serializers.BooleanField(default=True, help_text='是否HTML格式')


class SharePointOperationSerializer(serializers.Serializer):
    """SharePoint操作"""
    
    OPERATION_CHOICES = [
        ('get_site', '获取站点'),
        ('list_lists', '列出列表'),
        ('get_items', '获取列表项'),
    ]
    
    token_id = serializers.IntegerField(required=False, help_text='API Token ID，不提供则使用默认')
    operation = serializers.ChoiceField(choices=OPERATION_CHOICES)
    site_id = serializers.CharField(help_text='站点ID')
    list_id = serializers.CharField(required=False, help_text='列表ID（获取列表项时必需）')

