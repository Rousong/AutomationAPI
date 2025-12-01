"""
初始化常用的API端点
"""
from django.core.management.base import BaseCommand
from microsoft_api.models import APIEndpoint


class Command(BaseCommand):
    help = '初始化常用的微软API端点'
    
    def handle(self, *args, **options):
        endpoints = [
            # Teams相关端点
            {
                'name': 'Teams - 发送频道消息',
                'service': 'teams',
                'endpoint_url': 'teams/{team_id}/channels/{channel_id}/messages',
                'http_method': 'POST',
                'requires_body': True,
                'description': '向Teams频道发送消息'
            },
            {
                'name': 'Teams - 发送聊天消息',
                'service': 'teams',
                'endpoint_url': 'chats/{chat_id}/messages',
                'http_method': 'POST',
                'requires_body': True,
                'description': '向Teams聊天发送消息'
            },
            {
                'name': 'Teams - 列出加入的团队',
                'service': 'teams',
                'endpoint_url': 'me/joinedTeams',
                'http_method': 'GET',
                'requires_body': False,
                'description': '获取用户加入的所有团队'
            },
            {
                'name': 'Teams - 列出频道',
                'service': 'teams',
                'endpoint_url': 'teams/{team_id}/channels',
                'http_method': 'GET',
                'requires_body': False,
                'description': '获取团队的所有频道'
            },
            
            # Outlook相关端点
            {
                'name': 'Outlook - 发送邮件',
                'service': 'outlook',
                'endpoint_url': 'me/sendMail',
                'http_method': 'POST',
                'requires_body': True,
                'description': '发送邮件'
            },
            {
                'name': 'Outlook - 获取收件箱邮件',
                'service': 'outlook',
                'endpoint_url': 'me/mailFolders/inbox/messages',
                'http_method': 'GET',
                'requires_body': False,
                'description': '获取收件箱邮件列表'
            },
            {
                'name': 'Outlook - 获取邮件文件夹',
                'service': 'outlook',
                'endpoint_url': 'me/mailFolders',
                'http_method': 'GET',
                'requires_body': False,
                'description': '获取所有邮件文件夹'
            },
            
            # SharePoint相关端点
            {
                'name': 'SharePoint - 获取站点信息',
                'service': 'sharepoint',
                'endpoint_url': 'sites/{site_id}',
                'http_method': 'GET',
                'requires_body': False,
                'description': '获取SharePoint站点信息'
            },
            {
                'name': 'SharePoint - 列出站点列表',
                'service': 'sharepoint',
                'endpoint_url': 'sites/{site_id}/lists',
                'http_method': 'GET',
                'requires_body': False,
                'description': '获取站点的所有列表'
            },
            {
                'name': 'SharePoint - 获取列表项',
                'service': 'sharepoint',
                'endpoint_url': 'sites/{site_id}/lists/{list_id}/items',
                'http_method': 'GET',
                'requires_body': False,
                'description': '获取列表中的所有项'
            },
            {
                'name': 'SharePoint - 上传文件',
                'service': 'sharepoint',
                'endpoint_url': 'sites/{site_id}/drives/{drive_id}/root:/{file_path}:/content',
                'http_method': 'PUT',
                'requires_body': True,
                'description': '上传文件到SharePoint'
            },
            {
                'name': 'SharePoint - 获取文档库',
                'service': 'sharepoint',
                'endpoint_url': 'sites/{site_id}/drives',
                'http_method': 'GET',
                'requires_body': False,
                'description': '获取站点的文档库'
            },
            
            # Microsoft Graph通用端点
            {
                'name': 'Graph - 获取用户信息',
                'service': 'graph',
                'endpoint_url': 'me',
                'http_method': 'GET',
                'requires_body': False,
                'description': '获取当前用户信息'
            },
            {
                'name': 'Graph - 列出用户',
                'service': 'graph',
                'endpoint_url': 'users',
                'http_method': 'GET',
                'requires_body': False,
                'description': '列出组织中的用户'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for endpoint_data in endpoints:
            endpoint, created = APIEndpoint.objects.update_or_create(
                name=endpoint_data['name'],
                defaults=endpoint_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 创建端点: {endpoint.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'→ 更新端点: {endpoint.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！创建了 {created_count} 个端点，更新了 {updated_count} 个端点。'
            )
        )

