from django.db import models
import secrets
from django.contrib.auth.models import User

# ==================== BASE MODEL ====================
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

# ==================== CATEGORY ====================
class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nomi')
    description = models.TextField(blank=True, null=True, verbose_name='Tavsif')

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'

    def __str__(self):
        return self.name
    
    def product_count(self):
        return self.products.count()
    product_count.short_description = 'Mahsulotlar soni'

# ==================== PRODUCT ====================
class Product(BaseModel):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name='Kategoriya')
    name = models.CharField(max_length=200, verbose_name='Nomi')
    description = models.TextField(verbose_name='Tavsif', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Narxi')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Eski narxi (Agar bo\'lsa)')
    stock = models.IntegerField(blank=True, null=True, verbose_name='Ombordagi miqdor')
    image = models.ImageField(upload_to='store/products/', blank=True, null=True, verbose_name='Rasm')
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'

    def get_price_action_percent(self):
        if self.old_price and self.old_price > self.price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount, 2)
        return 0


    def __str__(self):
        return self.name


# ==================== COURIER ====================
class Courier(models.Model):
    """Kuryer modeli - Telegram bot orqali ro'yxatdan o'tadi"""
    
    REGION_CHOICES = [
        ('tashkent', 'Toshkent'),
        ('samarkand', 'Samarqand'),
        ('bukhara', 'Buxoro'),
        ('andijan', 'Andijon'),
        ('fergana', 'Farg\'ona'),
        ('namangan', 'Namangan'),
        ('kashkadarya', 'Qashqadaryo'),
        ('surkhandarya', 'Surxondaryo'),
        ('jizzakh', 'Jizzax'),
        ('syrdarya', 'Sirdaryo'),
        ('navoiy', 'Navoiy'),
        ('khorezm', 'Xorazm'),
        ('karakalpakstan', 'Qoraqalpog\'iston'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('active', 'Faol'),
        ('inactive', 'Faol emas'),
        ('blocked', 'Bloklangan'),
    ]
    
    # Asosiy ma'lumotlar
    first_name = models.CharField('Ism', max_length=100)
    last_name = models.CharField('Familiya', max_length=100)
    phone = models.CharField('Telefon', max_length=20, unique=True)
    telegram_id = models.BigIntegerField('Telegram ID', unique=True, null=True, blank=True)
    telegram_username = models.CharField('Telegram username', max_length=100, blank=True)
    
    # Hudud
    region = models.CharField('Viloyat', max_length=50, choices=REGION_CHOICES)
    
    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Statistika
    total_orders = models.IntegerField('Jami buyurtmalar', default=0)
    completed_orders = models.IntegerField('Yetkazilgan', default=0)
    cancelled_orders = models.IntegerField('Bekor qilingan', default=0)
    
    # Sanalar
    created_at = models.DateTimeField('Ro\'yxatdan o\'tgan', auto_now_add=True)
    updated_at = models.DateTimeField('Yangilangan', auto_now=True)
    last_active = models.DateTimeField('Oxirgi faollik', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Kuryer'
        verbose_name_plural = 'Kuryerlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_region_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def success_rate(self):
        """Muvaffaqiyat foizi"""
        if self.total_orders == 0:
            return 0
        return round((self.completed_orders / self.total_orders) * 100, 1)


# ==================== COURIER TOKEN ====================
class CourierToken(models.Model):
    """Bir martalik token - kuryer ro'yxatdan o'tish uchun"""
    
    token = models.CharField('Token', max_length=64, unique=True, db_index=True)
    is_used = models.BooleanField('Ishlatilgan', default=False)
    used_by = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True, related_name='tokens')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tokens')
    created_at = models.DateTimeField('Yaratilgan', auto_now_add=True)
    expires_at = models.DateTimeField('Amal qilish muddati')
    used_at = models.DateTimeField('Ishlatilgan vaqt', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Kuryer Tokeni'
        verbose_name_plural = 'Kuryer Tokenlari'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Token: {self.token[:20]}... ({'Ishlatilgan' if self.is_used else 'Faol'})"
    
    @classmethod
    def generate_token(cls, created_by):
        """Yangi token yaratish"""
        from datetime import timedelta
        from django.utils import timezone
        
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        
        return cls.objects.create(
            token=token,
            created_by=created_by,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """Token hali amal qiladimi?"""
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()


# ==================== ORDER ====================
class Order(models.Model):
    """Buyurtma modeli - Bot va website integratsiyasi uchun"""
    
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),          # Yangi buyurtma
        ('accepted', 'Qabul qilingan'),     # Kuryer qabul qildi
        ('delivering', 'Yo\'lda'),          # Kuryer yetkazmoqda
        ('delivered', 'Yetkazilgan'),       # Yetkazib berildi
        ('cancelled', 'Bekor qilingan'),    # Bekor qilindi
    ]

    PAYMENT_METHODS = [
        ('naqd', 'Naqd'),
        ('karta', 'Karta orqali'),
        ('click', 'Click / Payme'),
        ('bank', 'Bank orqali'),
    ]

    # Asosiy ma'lumotlar
    order_id = models.CharField(max_length=20, unique=True, verbose_name="Buyurtma ID")
    courier = models.ForeignKey(
        Courier, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orders',
        verbose_name="Kuryer"
    )
    products = models.ManyToManyField('Product', verbose_name="Mahsulotlar") 
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umumiy narx")
    
    # Mijoz ma'lumotlari
    full_name = models.CharField(max_length=120, verbose_name="Ism Familya")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqam")
    address = models.CharField(max_length=255, verbose_name="Manzil", blank=True, null=True)
    region = models.CharField(max_length=120, verbose_name="Viloyat", blank=True, null=True)
    district = models.CharField(max_length=120, verbose_name="Tuman", blank=True, null=True)
    
    # To'lov va qo'shimcha
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="To'lov usuli")
    comments = models.TextField(verbose_name="Qo'shimcha izohlar", blank=True, null=True)
    
    # Status va sanalar
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holat")
    created_at = models.DateTimeField('Yaratilgan', auto_now_add=True)
    accepted_at = models.DateTimeField('Qabul qilingan', null=True, blank=True)
    delivering_at = models.DateTimeField('Yo\'lga chiqdi', null=True, blank=True)
    delivered_at = models.DateTimeField('Yetkazilgan', null=True, blank=True)
    cancelled_at = models.DateTimeField('Bekor qilingan', null=True, blank=True)
    
    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_id:
            import uuid
            self.order_id = str(uuid.uuid4()).replace('-', '').upper()[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.order_id} - {self.full_name}"