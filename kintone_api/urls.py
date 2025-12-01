"""
Kintone API应用的URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'connections', views.KintoneConnectionViewSet, basename='kintone-connection')
router.register(r'apps', views.KintoneAppViewSet, basename='kintone-app')
router.register(r'logs', views.KintoneRequestLogViewSet, basename='kintone-log')
router.register(r'field-mappings', views.KintoneFieldMappingViewSet, basename='kintone-fieldmapping')
router.register(r'kintone', views.KintoneAPIViewSet, basename='kintone-api')

urlpatterns = [
    path('', include(router.urls)),
]

