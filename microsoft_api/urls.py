"""
Microsoft API应用的URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tokens', views.APITokenViewSet, basename='apitoken')
router.register(r'endpoints', views.APIEndpointViewSet, basename='apiendpoint')
router.register(r'logs', views.APIUsageLogViewSet, basename='apiusagelog')
router.register(r'teams-messages', views.TeamsMessageViewSet, basename='teamsmessage')
router.register(r'email-templates', views.EmailTemplateViewSet, basename='emailtemplate')
router.register(r'microsoft', views.MicrosoftAPIViewSet, basename='microsoft')

urlpatterns = [
    path('', include(router.urls)),
]

