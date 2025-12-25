"""
Management command to fix ACL for existing files in Supabase S3
Usage: python manage.py fix_s3_acl
"""
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings
import boto3
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'Fix ACL for all files in Supabase S3 bucket to public-read'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting ACL fix for Supabase S3...'))
        
        # S3 client yaratish
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        prefix = 'media/'  # Media fayllar
        
        try:
            # Bucket ichidagi barcha objectlarni olish
            paginator = s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
            
            fixed_count = 0
            error_count = 0
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    key = obj['Key']
                    try:
                        # ACL'ni public-read ga o'zgartirish
                        s3_client.put_object_acl(
                            Bucket=bucket_name,
                            Key=key,
                            ACL='public-read'
                        )
                        fixed_count += 1
                        self.stdout.write(self.style.SUCCESS(f'✓ Fixed ACL for: {key}'))
                    except ClientError as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(f'✗ Error fixing {key}: {e}'))
            
            self.stdout.write(self.style.SUCCESS(
                f'\nCompleted! Fixed: {fixed_count} files, Errors: {error_count}'
            ))
            
            # Bucket policy'ni ham sozlash
            self.stdout.write(self.style.SUCCESS('\nSetting bucket policy...'))
            try:
                bucket_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PublicReadGetObject",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/media/*"
                        }
                    ]
                }
                
                s3_client.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=str(bucket_policy).replace("'", '"')
                )
                self.stdout.write(self.style.SUCCESS('✓ Bucket policy set successfully!'))
            except ClientError as e:
                self.stdout.write(self.style.WARNING(
                    f'⚠ Could not set bucket policy: {e}\n'
                    'You may need to set it manually in Supabase dashboard.'
                ))
                
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'Error accessing S3: {e}'))

