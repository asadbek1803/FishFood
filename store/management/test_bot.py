# store/management/commands/test_bot.py
import asyncio
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Test bot connection and webhook status'

    def handle(self, *args, **options):
        asyncio.run(self.async_handle())

    async def async_handle(self):
        from bot.bot import get_application
        
        try:
            self.stdout.write("Getting bot application...")
            app = await get_application()
            
            self.stdout.write("Testing bot connection...")
            me = await app.bot.get_me()
            self.stdout.write(self.style.SUCCESS(f"✅ Bot connected: @{me.username} ({me.first_name})"))
            
            self.stdout.write("\nChecking webhook info...")
            webhook_info = await app.bot.get_webhook_info()
            
            self.stdout.write(f"\nWebhook Status:")
            self.stdout.write(f"  URL: {webhook_info.url or 'Not set'}")
            self.stdout.write(f"  Pending updates: {webhook_info.pending_update_count}")
            self.stdout.write(f"  Max connections: {webhook_info.max_connections}")
            
            if webhook_info.last_error_date:
                self.stdout.write(self.style.WARNING(
                    f"  Last error: {webhook_info.last_error_message} "
                    f"(at {webhook_info.last_error_date})"
                ))
            
            if webhook_info.allowed_updates:
                self.stdout.write(f"  Allowed updates: {webhook_info.allowed_updates}")
            
            if not webhook_info.url:
                self.stdout.write(self.style.WARNING(
                    "\n⚠️  Webhook not set! Use: python manage.py set_webhook --url <URL>"
                ))
            else:
                self.stdout.write(self.style.SUCCESS("\n✅ Webhook is configured"))
            
            # Test sending a message (optional)
            chat_id = input("\nEnter your Telegram user ID to test message sending (or press Enter to skip): ").strip()
            if chat_id:
                try:
                    chat_id = int(chat_id)
                    await app.bot.send_message(
                        chat_id=chat_id,
                        text="🔔 Test message from bot!\n\nIf you see this, the bot is working correctly."
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Test message sent to {chat_id}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Failed to send message: {e}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
            import traceback
            traceback.print_exc()