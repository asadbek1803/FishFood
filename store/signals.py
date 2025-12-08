# store/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def new_order_notify(sender, instance, created, **kwargs):
    """Yangi buyurtma yaratilganda kuryerlarga xabar yuborish"""
    
    # Faqat yangi buyurtmalar uchun
    if not created:
        return
    
    # Faqat pending statusdagi buyurtmalar uchun
    if instance.status != 'pending':
        return
    
    try:
        logger.info(f"📦 Yangi buyurtma yaratildi: #{instance.order_id}")
        
        # Views'dan sync wrapper funksiyani chaqirish
        from store.views import send_courier_notification_sync
        send_courier_notification_sync(instance)
        
    except Exception as e:
        logger.error(f"❌ Signal handler error: {e}", exc_info=True)