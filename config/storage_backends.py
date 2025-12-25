"""
Railway S3 Storage Backend
Railway S3 uchun maxsus storage backend
"""
import os
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
from urllib.parse import urljoin


class RailwayS3Storage(S3Boto3Storage):
    """
    Railway S3 Storage Backend
    Railway S3'ning S3-compatible API'si bilan ishlash uchun
    
    Railway S3 URL format: https://storage.railway.app/bucket-name/path/to/file
    """
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Railway S3 endpoint URL ni to'g'ri sozlash
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
        Railway S3'da public access uchun ACL'ni to'g'ri o'rnatish
        """
        # Name'ni normalize qilish
        name = self._normalize_name(name)
        
        # Content-Type'ni aniqlash
        import mimetypes
        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # ExtraArgs parametrlari
        extra_args = {
            'ACL': self.default_acl or 'public-read',
            'ContentType': content_type,
        }
        
        # Object parameters ni qo'shish
        if hasattr(settings, 'AWS_S3_OBJECT_PARAMETERS'):
            extra_args.update(settings.AWS_S3_OBJECT_PARAMETERS)
        
        # Boto3 orqali yuklash
        obj = self.bucket.Object(name)
        obj.upload_fileobj(content, ExtraArgs=extra_args)
        
        return name
    
    def url(self, name):
        """
        Railway S3 uchun to'g'ri URL generatsiya qilish
        Format: https://storage.railway.app/bucket-name/media/file.jpg
        """
        # Railway S3 uchun maxsus URL format
        if self.endpoint_url and self.bucket_name:
            # Name'ni normalize qilish
            name = self._normalize_name(name)
            
            # Location va name'ni birlashtirish
            if self.location:
                if name.startswith(self.location):
                    file_path = name
                else:
                    file_path = f'{self.location}/{name}'
            else:
                file_path = name
            
            # Railway S3 URL format: endpoint/bucket/path
            url = f'{self.endpoint_url.rstrip("/")}/{self.bucket_name}/{file_path}'
            return url
        
        # Agar sozlamalar bo'lmasa, odatiy S3 URL ishlatish
        return super().url(name)

