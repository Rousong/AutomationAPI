"""
单元测试
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import APIToken, APIEndpoint, APIUsageLog


class APITokenModelTest(TestCase):
    """API Token模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = APIToken.objects.create(
            name='测试Token',
            client_id='test-client-id',
            client_secret='test-secret',
            tenant_id='test-tenant-id',
            created_by=self.user
        )
    
    def test_token_creation(self):
        """测试Token创建"""
        self.assertEqual(self.token.name, '测试Token')
        self.assertTrue(self.token.is_active)
    
    def test_token_string_representation(self):
        """测试Token字符串表示"""
        self.assertEqual(str(self.token), '测试Token (活跃)')
    
    def test_token_validity_check(self):
        """测试Token有效性检查"""
        self.assertFalse(self.token.is_token_valid())


class APIEndpointModelTest(TestCase):
    """API端点模型测试"""
    
    def setUp(self):
        self.endpoint = APIEndpoint.objects.create(
            name='测试端点',
            service='teams',
            endpoint_url='teams/test',
            http_method='GET'
        )
    
    def test_endpoint_creation(self):
        """测试端点创建"""
        self.assertEqual(self.endpoint.name, '测试端点')
        self.assertEqual(self.endpoint.service, 'teams')
        self.assertTrue(self.endpoint.is_active)
    
    def test_endpoint_total_calls_default(self):
        """测试端点调用次数默认值"""
        self.assertEqual(self.endpoint.total_calls, 0)


class APITokenViewSetTest(APITestCase):
    """API Token视图集测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.token_data = {
            'name': 'API测试Token',
            'client_id': 'test-id',
            'client_secret': 'test-secret',
            'tenant_id': 'test-tenant',
            'is_active': True
        }
    
    def test_list_tokens(self):
        """测试列出Token"""
        response = self.client.get('/api/tokens/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_token(self):
        """测试创建Token"""
        response = self.client.post('/api/tokens/', self.token_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(APIToken.objects.count(), 1)
    
    def test_create_token_unauthorized(self):
        """测试未认证创建Token"""
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/tokens/', self.token_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class APIEndpointViewSetTest(APITestCase):
    """API端点视图集测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.endpoint = APIEndpoint.objects.create(
            name='测试端点',
            service='teams',
            endpoint_url='teams/test',
            http_method='GET'
        )
    
    def test_list_endpoints(self):
        """测试列出端点"""
        response = self.client.get('/api/endpoints/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_endpoints_by_service(self):
        """测试按服务筛选端点"""
        response = self.client.get('/api/endpoints/?service=teams')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_endpoint_statistics(self):
        """测试端点统计"""
        response = self.client.get('/api/endpoints/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIUsageLogTest(TestCase):
    """API使用日志测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.token = APIToken.objects.create(
            name='测试Token',
            client_id='test-id',
            client_secret='test-secret',
            tenant_id='test-tenant'
        )
        
        self.endpoint = APIEndpoint.objects.create(
            name='测试端点',
            service='teams',
            endpoint_url='teams/test',
            http_method='GET'
        )
        
        self.log = APIUsageLog.objects.create(
            endpoint=self.endpoint,
            token=self.token,
            request_method='GET',
            request_url='https://graph.microsoft.com/v1.0/teams/test',
            status_code=200,
            response_time=0.5,
            status='success',
            user=self.user
        )
    
    def test_log_creation(self):
        """测试日志创建"""
        self.assertEqual(self.log.status, 'success')
        self.assertEqual(self.log.status_code, 200)
    
    def test_log_string_representation(self):
        """测试日志字符串表示"""
        self.assertIn('测试端点', str(self.log))
        self.assertIn('success', str(self.log))
