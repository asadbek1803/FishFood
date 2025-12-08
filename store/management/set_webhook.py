# store/management/commands/set_webhook.py
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Set Telegram webhook URL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='Webhook URL (e.g., https://yourdomain.com/store/bot/webhook/)',
            required=True
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete webhook instead of setting it'
        )

    def handle(self, *args, **options):
        asyncio.run(self.async_handle(options))

    async def async_handle(self, options):
        from bot.bot import get_application
        
        app = await get_application()
        
        if options['delete']:
            self.stdout.write('Deleting webhook...')
            result = await app.bot.delete_webhook(drop_pending_updates=True)
            if result:
                self.stdout.write(self.style.SUCCESS('✅ Webhook deleted successfully'))
            else:
                self.stdout.write(self.style.ERROR('❌ Failed to delete webhook'))
        else:
            webhook_url = options['url']
            self.stdout.write(f'Setting webhook to: {webhook_url}')
            
            result = await app.bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS('✅ Webhook set successfully'))
                
                # Verify webhook
                webhook_info = await app.bot.get_webhook_info()
                self.stdout.write(f'\nWebhook info:')
                self.stdout.write(f'  URL: {webhook_info.url}')
                self.stdout.write(f'  Pending updates: {webhook_info.pending_update_count}')
                if webhook_info.last_error_message:
                    self.stdout.write(self.style.WARNING(
                        f'  Last error: {webhook_info.last_error_message}'
                    ))
            else:
                self.stdout.write(self.style.ERROR('❌ Failed to set webhook'))