# store/apps.py
from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    verbose_name = 'Magazin'
    
    def ready(self):
        """Django ishga tushganda signallarni import qilish"""
        # Signallarni import qilish
        import store.signals  # noqa
        
        # Log chiqarish
        import logging
        logger = logging.getLogger(__name__)
        logger.info("🟢 Store app tayyor")