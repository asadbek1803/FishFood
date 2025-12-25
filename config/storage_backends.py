"""
Supabase S3 Storage Backend
Supabase S3 uchun maxsus storage backend
"""
import os
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
from urllib.parse import urljoin


class RailwayS3Storage(S3Boto3Storage):
    """
    Supabase S3 Storage Backend
    Supabase S3'ning S3-compatible API'si bilan ishlash uchun
    
    Supabase S3 URL format: https://xikvlxlkhysjfarzonsa.storage.supabase.co/storage/v1/s3/bucket-name/path/to/file
    """
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Supabase S3 endpoint URL ni to'g'ri sozlash
        self.endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
        self.bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    
    def _normalize_name(self, name):
        """
        Fayl nomini normalize qilish
        """
        return super()._normalize_name(name)
    
    def _save(self, name, content):
        """
        Faylni saqlash va ACL'ni to'g'ri sozlash
        Supabase S3'da public access uchun ACL'ni to'g'ri o'rnatish
        """
        # Name'ni normalize qilish
        name = self._normalize_name(name)
        
        # Content-Type'ni aniqlash
        import mimetypes
        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # ExtraArgs parametrlari - ACL'ni majburiy o'rnatish
        extra_args = {
            'ACL': 'public-read',  # Majburiy public-read
            'ContentType': content_type,
        }
        
        # Object parameters ni qo'shish (lekin ACL'ni override qilish)
        if hasattr(settings, 'AWS_S3_OBJECT_PARAMETERS'):
            params = settings.AWS_S3_OBJECT_PARAMETERS.copy()
            # ACL'ni saqlash
            if 'ACL' in params:
                extra_args['ACL'] = params['ACL']
            # Boshqa parametrlarni qo'shish
            for key, value in params.items():
                if key != 'ACL':
                    extra_args[key] = value
        
        # Boto3 orqali yuklash
        obj = self.bucket.Object(name)
        obj.upload_fileobj(content, ExtraArgs=extra_args)
        
        # ACL'ni yana bir marta tekshirish va o'rnatish (agar kerak bo'lsa)
        try:
            current_acl = obj.Acl().grants
            # Agar public-read bo'lmasa, o'rnatish
            has_public_read = any(
                grant.get('Grantee', {}).get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'
                for grant in current_acl
            )
            if not has_public_read:
                obj.Acl().put(ACL='public-read')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not verify/set ACL for {name}: {e}")
        
        return name
    
    def url(self, name):
        """
        Supabase S3 uchun to'g'ri URL generatsiya qilish
        Path-style: https://xikvlxlkhysjfarzonsa.storage.supabase.co/storage/v1/s3/bucket-name/media/file.jpg
        """
        # Name'ni normalize qilish
        name = self._normalize_name(name)
        
        # Path-style URL generatsiya qilish (Supabase S3 uchun)
        if self.endpoint_url and self.bucket_name:
            # Location va name'ni birlashtirish
            if self.location:
                if name.startswith(self.location):
                    file_path = name
                else:
                    file_path = f'{self.location}/{name}'
            else:
                file_path = name
            
            # Supabase S3 URL format: endpoint/bucket/path
            # Endpoint allaqachon /storage/v1/s3 ni o'z ichiga oladi
            url = f'{self.endpoint_url.rstrip("/")}/{self.bucket_name}/{file_path}'
            return url
        
        # Agar sozlamalar bo'lmasa, odatiy S3 URL ishlatish
        return super().url(name)

