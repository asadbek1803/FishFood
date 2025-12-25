"""
Management command to create Supabase bucket if it doesn't exist
Usage: python manage.py create_supabase_bucket
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'Create Supabase S3 bucket if it does not exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bucket-name',
            type=str,
            default=None,
            help='Bucket name to create (default: from settings)',
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='Make bucket public (default: True)',
        )

    def handle(self, *args, **options):
        bucket_name = options.get('bucket_name') or settings.AWS_STORAGE_BUCKET_NAME
        is_public = options.get('public', True)
        
        self.stdout.write(self.style.SUCCESS(f'Creating Supabase bucket: {bucket_name}...'))
        
        # S3 client yaratish
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        
        try:
            # Bucket mavjudligini tekshirish
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                self.stdout.write(self.style.WARNING(f'Bucket "{bucket_name}" already exists!'))
                return
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code != '404':
                    # Boshqa xato
                    raise
            
            # Bucket yaratish
            if settings.AWS_S3_REGION_NAME and settings.AWS_S3_REGION_NAME != 'auto':
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': settings.AWS_S3_REGION_NAME
                    }
                )
            else:
                # Region yo'q bo'lsa, oddiy yaratish
                s3_client.create_bucket(Bucket=bucket_name)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Bucket "{bucket_name}" created successfully!'))
            
            # Public access uchun sozlash
            if is_public:
                try:
                    # Public access block settings ni o'chirish
                    s3_client.put_public_access_block(
                        Bucket=bucket_name,
                        PublicAccessBlockConfiguration={
                            'BlockPublicAcls': False,
                            'IgnorePublicAcls': False,
                            'BlockPublicPolicy': False,
                            'RestrictPublicBuckets': False,
                        }
                    )
                    self.stdout.write(self.style.SUCCESS('✓ Public access enabled!'))
                    
                    # Bucket policy'ni sozlash
                    bucket_policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "PublicReadGetObject",
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": "s3:GetObject",
                                "Resource": f"arn:aws:s3:::{bucket_name}/*"
                            }
                        ]
                    }
                    
                    s3_client.put_bucket_policy(
                        Bucket=bucket_name,
                        Policy=str(bucket_policy).replace("'", '"')
                    )
                    self.stdout.write(self.style.SUCCESS('✓ Bucket policy set for public access!'))
                except ClientError as e:
                    self.stdout.write(self.style.WARNING(
                        f'⚠ Could not set public access: {e}\n'
                        'You may need to set it manually in Supabase dashboard.'
                    ))
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            if error_code == 'BucketAlreadyOwnedByYou':
                self.stdout.write(self.style.WARNING(f'Bucket "{bucket_name}" already exists and is owned by you.'))
            else:
                self.stdout.write(self.style.ERROR(
                    f'Error creating bucket: {error_code} - {error_message}\n'
                    f'\nMake sure:\n'
                    f'1. Supabase Dashboard → Storage → Buckets bo\'limida bucket yaratilgan\n'
                    f'2. Bucket nomi to\'g\'ri: {bucket_name}\n'
                    f'3. Bucket public access enabled'
                ))

