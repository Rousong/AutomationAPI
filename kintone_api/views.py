"""
Kintone API视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import KintoneConnection, KintoneApp, KintoneRequestLog, KintoneFieldMapping
from .serializers import (
    KintoneConnectionSerializer, KintoneConnectionListSerializer,
    KintoneAppSerializer, KintoneRequestLogSerializer, KintoneRequestLogDetailSerializer,
    KintoneFieldMappingSerializer,
    KintoneGetRecordsSerializer, KintoneGetRecordSerializer,
    KintoneAddRecordSerializer, KintoneAddRecordsSerializer,
    KintoneUpdateRecordSerializer, KintoneUpdateRecordsSerializer,
    KintoneDeleteRecordsSerializer, KintoneGetAppInfoSerializer,
    KintoneGetFormFieldsSerializer
)
from .services import KintoneService


class KintoneConnectionViewSet(viewsets.ModelViewSet):
    """Kintone连接管理"""
    
    queryset = KintoneConnection.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return KintoneConnectionListSerializer
        return KintoneConnectionSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class KintoneAppViewSet(viewsets.ModelViewSet):
    """Kintone应用管理"""
    
    queryset = KintoneApp.objects.select_related('connection').all()
    serializer_class = KintoneAppSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        connection_id = self.request.query_params.get('connection', None)
        if connection_id:
            queryset = queryset.filter(connection_id=connection_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取应用统计信息"""
        stats = KintoneApp.objects.values('connection__name').annotate(
            total_apps=Count('id'),
            active_apps=Count('id', filter=Q(is_active=True)),
            total_requests=Count('logs')
        )
        return Response(stats)


class KintoneRequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Kintone请求日志（只读）"""
    
    queryset = KintoneRequestLog.objects.select_related(
        'connection', 'app', 'user'
    ).all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return KintoneRequestLogDetailSerializer
        return KintoneRequestLogSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 过滤参数
        app_id = self.request.query_params.get('app', None)
        action = self.request.query_params.get('action', None)
        status_filter = self.request.query_params.get('status', None)
        days = self.request.query_params.get('days', None)
        
        if app_id:
            queryset = queryset.filter(app_id=app_id)
        
        if action:
            queryset = queryset.filter(action=action)
        
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
        
        logs = KintoneRequestLog.objects.filter(created_at__gte=date_from)
        
        stats = {
            'total_requests': logs.count(),
            'success_requests': logs.filter(status='success').count(),
            'failed_requests': logs.filter(status='failed').count(),
            'error_requests': logs.filter(status='error').count(),
            'by_action': list(logs.values('action').annotate(
                count=Count('id')
            ).order_by('-count')),
            'by_app': list(logs.values('app__app_name').annotate(
                count=Count('id')
            ).order_by('-count')[:10]),
        }
        
        return Response(stats)


class KintoneFieldMappingViewSet(viewsets.ModelViewSet):
    """Kintone字段映射管理"""
    
    queryset = KintoneFieldMapping.objects.select_related('app').all()
    serializer_class = KintoneFieldMappingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        app_id = self.request.query_params.get('app', None)
        if app_id:
            queryset = queryset.filter(app_id=app_id)
        return queryset


class KintoneAPIViewSet(viewsets.ViewSet):
    """Kintone API操作视图集"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def get_records(self, request):
        """获取记录列表"""
        serializer = KintoneGetRecordsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        connection_id = data.get('connection_id')
        
        try:
            service = KintoneService(connection_id=connection_id)
            
            result = service.get_records(
                app_id=data['app_id'],
                query=data.get('query'),
                fields=data.get('fields'),
                total_count=data.get('total_count', False),
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': '记录获取成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def get_record(self, request):
        """获取单条记录"""
        serializer = KintoneGetRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        connection_id = data.get('connection_id')
        
        try:
            service = KintoneService(connection_id=connection_id)
            
            result = service.get_record(
                app_id=data['app_id'],
                record_id=data['record_id'],
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': '记录获取成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def add_record(self, request):
        """添加记录"""
        serializer = KintoneAddRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        connection_id = data.get('connection_id')
        
        try:
            service = KintoneService(connection_id=connection_id)
            
            result = service.add_record(
                app_id=data['app_id'],
                record_data=data['record_data'],
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': '记录添加成功',
                'data': result
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def add_records(self, request):
        """批量添加记录"""
        serializer = KintoneAddRecordsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        connection_id = data.get('connection_id')
        
        try:
            service = KintoneService(connection_id=connection_id)
            
            result = service.add_records(
                app_id=data['app_id'],
                records_data=data['records_data'],
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': f'成功添加 {len(data["records_data"])} 条记录',
                'data': result
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_record(self, request):
        """更新记录"""
        serializer = KintoneUpdateRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        connection_id = data.get('connection_id')
        
        try:
            service = KintoneService(connection_id=connection_id)
            
            result = service.update_record(
                app_id=data['app_id'],
                record_id=data['record_id'],
                record_data=data['record_data'],
                revision=data.get('revision'),
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': '记录更新成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_records(self, request):
        """批量更新记录"""
        serializer = KintoneUpdateRecordsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        connection_id = data.get('connection_id')
        
        try:
            service = KintoneService(connection_id=connection_id)
            
            result = service.update_records(
                app_id=data['app_id'],
                records_data=data['records_data'],
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': f'成功更新 {len(data["records_data"])} 条记录',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def delete_records(self, request):
        """删除记录"""
        serializer = KintoneDeleteRecordsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        connection_id = data.get('connection_id')
        
        try:
            service = KintoneService(connection_id=connection_id)
            
            result = service.delete_records(
                app_id=data['app_id'],
                record_ids=data['record_ids'],
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': f'成功删除 {len(data["record_ids"])} 条记录',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def get_app_info(self, request):
        """获取应用信息"""
        serializer = KintoneGetAppInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        connection_id = data.get('connection_id')
        
        try:
            service = KintoneService(connection_id=connection_id)
            
            result = service.get_app_info(
                app_id=data['app_id'],
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': '应用信息获取成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def get_form_fields(self, request):
        """获取表单字段"""
        serializer = KintoneGetFormFieldsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        connection_id = data.get('connection_id')
        
        try:
            service = KintoneService(connection_id=connection_id)
            
            result = service.get_form_fields(
                app_id=data['app_id'],
                user=request.user
            )
            
            return Response({
                'status': 'success',
                'message': '表单字段获取成功',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
