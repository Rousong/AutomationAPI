"""
REST API视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import APIToken, APIEndpoint, APIUsageLog, TeamsMessage, EmailTemplate
from .serializers import (
    APITokenSerializer, APITokenListSerializer, APIEndpointSerializer,
    APIUsageLogSerializer, APIUsageLogDetailSerializer,
    TeamsMessageSerializer, EmailTemplateSerializer,
    SendTeamsMessageSerializer, SendEmailSerializer, SharePointOperationSerializer
)
from .services import TeamsService, OutlookService, SharePointService


class APITokenViewSet(viewsets.ModelViewSet):
    """API Token管理"""
    
    queryset = APIToken.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return APITokenListSerializer
        return APITokenSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class APIEndpointViewSet(viewsets.ModelViewSet):
    """API端点管理"""
    
    queryset = APIEndpoint.objects.all()
    serializer_class = APIEndpointSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        service = self.request.query_params.get('service', None)
        if service:
            queryset = queryset.filter(service=service)
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取端点统计信息"""
        stats = APIEndpoint.objects.values('service').annotate(
            total_endpoints=Count('id'),
            active_endpoints=Count('id', filter=Q(is_active=True)),
            total_calls=Count('usage_logs')
        )
        return Response(stats)


class APIUsageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API使用日志（只读）"""
    
    queryset = APIUsageLog.objects.select_related('endpoint', 'token', 'user').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return APIUsageLogDetailSerializer
        return APIUsageLogSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 过滤参数
        endpoint_id = self.request.query_params.get('endpoint', None)
        status_filter = self.request.query_params.get('status', None)
        days = self.request.query_params.get('days', None)
        
        if endpoint_id:
            queryset = queryset.filter(endpoint_id=endpoint_id)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if days:
            date_from = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=date_from)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取使用统计"""
        days = int(request.query_params.get('days', 7))
        date_from = timezone.now() - timedelta(days=days)
        
        logs = APIUsageLog.objects.filter(created_at__gte=date_from)
        
        stats = {
            'total_calls': logs.count(),
            'success_calls': logs.filter(status='success').count(),
            'failed_calls': logs.filter(status='failed').count(),
            'error_calls': logs.filter(status='error').count(),
            'by_endpoint': list(logs.values('endpoint__name').annotate(
                count=Count('id')
            ).order_by('-count')[:10]),
            'by_service': list(logs.values('endpoint__service').annotate(
                count=Count('id')
            )),
        }
        
        return Response(stats)


class TeamsMessageViewSet(viewsets.ModelViewSet):
    """Teams消息模板管理"""
    
    queryset = TeamsMessage.objects.all()
    serializer_class = TeamsMessageSerializer
    permission_classes = [IsAuthenticated]


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """邮件模板管理"""
    
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]


class MicrosoftAPIViewSet(viewsets.ViewSet):
    """微软API操作视图集"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def send_teams_message(self, request):
        """发送Teams消息"""
        serializer = SendTeamsMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        token_id = data.get('token_id')
        
        try:
            service = TeamsService(token_id=token_id)
            
            if data['message_type'] == 'channel':
                result = service.send_channel_message(
                    team_id=data['team_id'],
                    channel_id=data['channel_id'],
                    message=data['message'],
                    user=request.user
                )
            else:  # chat
                result = service.send_chat_message(
                    chat_id=data['chat_id'],
                    message=data['message'],
                    user=request.user
                )
            
            return Response({
                'status': 'success',
                'message': 'Teams消息发送成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def send_email(self, request):
        """发送邮件"""
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        token_id = data.get('token_id')
        
        try:
            service = OutlookService(token_id=token_id)
            
            result = service.send_email(
                to_recipients=data['to_recipients'],
                subject=data['subject'],
                body=data['body'],
                cc_recipients=data.get('cc_recipients'),
                is_html=data.get('is_html', True),
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': '邮件发送成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def sharepoint_operation(self, request):
        """SharePoint操作"""
        serializer = SharePointOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        token_id = data.get('token_id')
        
        try:
            service = SharePointService(token_id=token_id)
            
            operation = data['operation']
            site_id = data['site_id']
            
            if operation == 'get_site':
                result = service.get_site(site_id, user=request.user)
            elif operation == 'list_lists':
                result = service.list_site_lists(site_id, user=request.user)
            elif operation == 'get_items':
                list_id = data.get('list_id')
                if not list_id:
                    raise ValueError("获取列表项需要提供list_id")
                result = service.get_list_items(site_id, list_id, user=request.user)
            else:
                raise ValueError(f"不支持的操作: {operation}")
            
            return Response({
                'status': 'success',
                'message': 'SharePoint操作成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def list_teams(self, request):
        """列出Teams团队"""
        token_id = request.query_params.get('token_id')
        
        try:
            service = TeamsService(token_id=token_id)
            result = service.list_teams(user=request.user)
            
            return Response({
                'status': 'success',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def list_emails(self, request):
        """列出邮件"""
        token_id = request.query_params.get('token_id')
        folder = request.query_params.get('folder', 'inbox')
        top = int(request.query_params.get('top', 10))
        
        try:
            service = OutlookService(token_id=token_id)
            result = service.list_messages(folder=folder, top=top, user=request.user)
            
            return Response({
                'status': 'success',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
