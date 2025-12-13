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