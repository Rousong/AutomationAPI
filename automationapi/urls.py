"""
URL configuration for automationapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    """API根视图"""
    return Response({
        'message': 'AutomationAPI - 微软API自动化管理系统',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'tokens': '/api/tokens/',
            'endpoints': '/api/endpoints/',
            'logs': '/api/logs/',
            'teams_messages': '/api/teams-messages/',
            'email_templates': '/api/email-templates/',
            'microsoft_api': {
                'send_teams_message': '/api/microsoft/send_teams_message/',
                'send_email': '/api/microsoft/send_email/',
                'sharepoint_operation': '/api/microsoft/sharepoint_operation/',
                'list_teams': '/api/microsoft/list_teams/',
                'list_emails': '/api/microsoft/list_emails/',
            }
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('microsoft_api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('', api_root, name='api-root'),
]
