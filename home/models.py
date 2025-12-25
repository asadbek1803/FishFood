from django.db import models

# ==================== BASE MODEL ====================
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

########################## Bosh sahifa modeli ##########################

class HomeSlider(BaseModel):
    SLIDER_TYPE_CHOICES = [
        ('image', 'Rasm'),
        ('video', 'Video'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif", blank=True)
    button_text = models.CharField(max_length=50, default="Batafsil", verbose_name="Tugma matni")
    button_url = models.CharField(max_length=200, default="/", verbose_name="Tugma havolasi")
    slider_type = models.CharField(max_length=10, choices=SLIDER_TYPE_CHOICES, default='image', verbose_name="Slider turi")
    
    # Image field
    image = models.ImageField(upload_to='sliders/', blank=True, null=True, verbose_name="Rasm")
    
    # Video field
    video = models.FileField(upload_to='slider_videos/', blank=True, null=True, verbose_name="Video fayl")
    video_url = models.URLField(blank=True, verbose_name="Video URL (YouTube, Vimeo)")
    
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    order = models.IntegerField(default=0, verbose_name="Tartib raqami")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Slider"
        verbose_name_plural = "Sliderlar"
    
    def __str__(self):
        return self.title
    
    def get_media_url(self):
        if self.slider_type == 'video':
            if self.video:
                return self.video.url
            elif self.video_url:
                return self.video_url
        elif self.image:
            return self.image.url
        return None

class Service(BaseModel):
    icon = models.CharField(max_length=100, verbose_name="Ikonka")
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif")

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Xizmat'
        verbose_name_plural = 'Xizmatlar'

    def __str__(self):
        return self.title


class Testimonial(BaseModel):
    full_name = models.CharField(max_length=100, verbose_name="To'liq ism")
    rate = models.IntegerField(verbose_name="Reyting (1-5)", choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField(verbose_name="Fikr-mulohaza")
    region = models.CharField(max_length=100, verbose_name="Hudud", blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Fikr-mulohaza'
        verbose_name_plural = 'Fikr-mulohazalar'

    def __str__(self):
        return self.full_name

######################## Site Setting Model ########################
class SiteSetting(BaseModel):
    title = models.CharField(max_length=200, verbose_name="Sayt nomi")
    logo = models.ImageField(upload_to='site/logo/', verbose_name="Sayt logotipi")
    description = models.TextField(verbose_name="Sayt tavsifi")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    email = models.EmailField(verbose_name="Elektron pochta")
    address = models.CharField(max_length=255, verbose_name="Manzil")
    facebook_url = models.URLField(max_length=200, blank=True, verbose_name="Facebook URL")
    telegram_url = models.URLField(max_length=200, blank=True, verbose_name="Telegram URL")
    instagram_url = models.URLField(max_length=200, blank=True, verbose_name="Instagram URL")
    youtube_url = models.URLField(max_length=200, blank=True, verbose_name="Youtube URL")

    class Meta:
        verbose_name = 'Sayt sozlamasi'
        verbose_name_plural = 'Sayt sozlamalari'

    def __str__(self):
        return self.title

######################## About Us Models ########################
class AboutUs(BaseModel):
    aboutUsImage = models.ImageField(upload_to='about/us/', verbose_name="Biz haqimizda rasmi")
    aboutUsTitle = models.CharField(max_length=200, verbose_name="Biz haqimizda sarlavhasi")
    aboutUsDescription = models.TextField(verbose_name="Biz haqimizda tavsifi")

    class Meta:
        verbose_name = 'Biz haqimizda'
        verbose_name_plural = 'Biz haqimizda'

    def __str__(self):
        return self.aboutUsTitle
    
class AboutUsMissons(BaseModel):
    missionIcon = models.CharField(max_length=100, verbose_name="Ikonka")
    missionTitle = models.CharField(max_length=200, verbose_name="Maqsad sarlavhasi")
    missionDescription = models.TextField(verbose_name="Maqsad tavsifi")

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Maqsad'
        verbose_name_plural = 'Maqsadlar'

    def __str__(self):
        return self.missionTitle

class AboutUsValues(BaseModel):
    valueIcon = models.CharField(max_length=100, verbose_name="Ikonka")
    valueTitle = models.CharField(max_length=200, verbose_name="Qadriyat sarlavhasi")
    valueDescription = models.TextField(verbose_name="Qadriyat tavsifi")

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Qadriyat'
        verbose_name_plural = 'Qadriyatlar'

    def __str__(self):
        return self.valueTitle


class AboutUsStats(BaseModel):
    statTitle = models.CharField(max_length=200, verbose_name="Statistika sarlavhasi")
    statValue = models.IntegerField(verbose_name="Statistika qiymati")

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Statistika'
        verbose_name_plural = 'Statistikalar'

    def __str__(self):
        return self.statTitle

class AboutUsTeam(BaseModel):
    teamImage = models.ImageField(upload_to='about/team/', verbose_name="Jamoa rasmi")
    teamFullName = models.CharField(max_length=100, verbose_name="To'liq ism")
    teamPosition = models.CharField(max_length=100, verbose_name="Lavozim")
    teamAbout = models.TextField(verbose_name="Jamoa a'zosi haqida (Ozroq ma'lumot)", help_text="Masalan: 20 yillik tajribaga ega dengiz mahsulotlari mutaxassisi", blank=True, null=True)


    class Meta:
        ordering = ['display_order']
        verbose_name = 'Jamoa a\'zosi'
        verbose_name_plural = 'Jamoa a\'zolari'

    def __str__(self):
        return self.teamFullName

class AboutUsQuestions(BaseModel):
    questionTitle = models.CharField(max_length=200, verbose_name="Savol", help_text="Qulay Narxlar")
    questionAnswer = models.TextField(verbose_name="Savol javobi", help_text="Sifatli mahsulotlarni hamyonbop narxlarda taklif qilamiz")

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Savol-Javob'
        verbose_name_plural = 'Savol-Javoblar'

    def __str__(self):
        return self.questionTitle

######################## Gallery Model ########################
class Gallery(BaseModel):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Rasm'),
        ('video', 'Video'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif", blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image', verbose_name="Media turi")
    
    # Image field
    image = models.ImageField(upload_to='gallery/images/', blank=True, null=True, verbose_name="Rasm")
    
    # Video field - katta fayllar uchun optimallashtirilgan
    video = models.FileField(
        upload_to='gallery/videos/', 
        blank=True, 
        null=True, 
        verbose_name="Video fayl",
        help_text="Maksimal hajm: 500MB. Katta videolar uchun video_url ishlatish tavsiya etiladi."
    )
    video_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="Video URL (YouTube, Vimeo)",
        help_text="YouTube yoki Vimeo video linkini kiriting. Bu katta videolar uchun yaxshiroq variant."
    )
    
    category = models.CharField(max_length=100, verbose_name="Kategoriya", blank=True, null=True, help_text="Masalan: Ish jarayonlari, Xabarlar, Mahsulotlar")
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Galereya'
        verbose_name_plural = 'Galereya'

    def __str__(self):
        return self.title
    
    def get_media_url(self):
        if self.media_type == 'video':
            if self.video:
                return self.video.url
            elif self.video_url:
                return self.video_url
        elif self.image:
            return self.image.url
        return None
    
    def get_thumbnail_url(self):
        if self.image:
            return self.image.url
        elif self.media_type == 'video':
            return None  # Video thumbnail uchun alohida yechim kerak
        return None

######################## SEO Metadata Model ########################
class SEOMetadata(BaseModel):
    PAGE_CHOICES = [
        ('home', 'Bosh sahifa'),
        ('about', 'Biz haqimizda'),
        ('gallery', 'Galereya'),
        ('shop', 'Mahsulotlar'),
        ('contact', 'Aloqa'),
    ]
    
    ROBOTS_CHOICES = [
        ('index, follow', 'Index va Follow'),
        ('index, nofollow', 'Index, no Follow'),
        ('noindex, follow', 'No Index, Follow'),
        ('noindex, nofollow', 'No Index, no Follow'),
    ]
    
    page = models.CharField(
        max_length=50,
        choices=PAGE_CHOICES,
        unique=True,
        verbose_name="Sahifa",
        help_text="Qaysi sahifa uchun SEO sozlamalar"
    )
    
    # Asosiy SEO
    meta_title = models.CharField(
        max_length=70,
        verbose_name="Meta Title",
        help_text="Sarlavha (maksimal 70 ta belgi). Qidiruv natijalarida ko'rinadi."
    )
    
    meta_description = models.TextField(
        max_length=160,
        verbose_name="Meta Description",
        help_text="Tavsif (maksimal 160 ta belgi). Qidiruv natijalarida ko'rinadi."
    )
    
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Meta Keywords",
        help_text="Kalit so'zlar (vergul bilan ajratilgan). Masalan: baliq, dengiz mahsulotlari, ikra"
    )
    
    # Robots Meta
    robots_meta = models.CharField(
        max_length=30,
        choices=ROBOTS_CHOICES,
        default='index, follow',
        verbose_name="Robots Meta",
        help_text="Qidiruv tizimlariga qanday ko'rsatma berish kerak"
    )
    
    # Canonical URL
    canonical_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Canonical URL",
        help_text="Agar bo'sh bo'lsa, avtomatik URL ishlatiladi"
    )
    
    # Open Graph (Facebook, LinkedIn)
    og_title = models.CharField(
        max_length=70,
        blank=True,
        null=True,
        verbose_name="OG Title",
        help_text="Ijtimoiy tarmoqlarda ko'rinadigan sarlavha"
    )
    
    og_description = models.TextField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="OG Description",
        help_text="Ijtimoiy tarmoqlarda ko'rinadigan tavsif"
    )
    
    og_image = models.ImageField(
        upload_to='seo/og_images/',
        blank=True,
        null=True,
        verbose_name="OG Image",
        help_text="Ijtimoiy tarmoqlarda ko'rinadigan rasm (1200x630px tavsiya qilinadi)"
    )
    
    og_type = models.CharField(
        max_length=50,
        default='website',
        verbose_name="OG Type",
        help_text="Masalan: website, article, product"
    )
    
    # Twitter Card
    twitter_card = models.CharField(
        max_length=20,
        choices=[
            ('summary', 'Summary'),
            ('summary_large_image', 'Summary Large Image'),
        ],
        default='summary_large_image',
        verbose_name="Twitter Card Type"
    )
    
    twitter_title = models.CharField(
        max_length=70,
        blank=True,
        null=True,
        verbose_name="Twitter Title"
    )
    
    twitter_description = models.TextField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Twitter Description"
    )
    
    twitter_image = models.ImageField(
        upload_to='seo/twitter_images/',
        blank=True,
        null=True,
        verbose_name="Twitter Image",
        help_text="Twitter'da ko'rinadigan rasm (1200x675px tavsiya qilinadi)"
    )
    
    # Structured Data (JSON-LD) - AI uchun
    structured_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Structured Data (JSON-LD)",
        help_text="Schema.org strukturali ma'lumotlar (AI va qidiruv tizimlari uchun)"
    )
    
    # Schema.org type
    schema_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Schema.org Type",
        help_text="Masalan: Organization, Product, Article, WebSite"
    )
    
    class Meta:
        verbose_name = 'SEO Metadata'
        verbose_name_plural = 'SEO Metadata'
        ordering = ['page']
    
    def __str__(self):
        return f"SEO: {self.get_page_display()}"
    
    def get_canonical_url(self, request=None):
        """Canonical URL ni qaytaradi"""
        if self.canonical_url:
            return self.canonical_url
        if request:
            return request.build_absolute_uri(request.path)
        return ''
    
    def get_og_image_url(self):
        """OG Image URL ni qaytaradi"""
        if self.og_image:
            return self.og_image.url
        return ''
    
    def get_twitter_image_url(self):
        """Twitter Image URL ni qaytaradi"""
        if self.twitter_image:
            return self.twitter_image.url
        return self.get_og_image_url()  # Agar bo'sh bo'lsa, OG image ishlatiladi