# admin.py
from django.contrib import admin
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import (
    HomeSlider, Service, Testimonial, SiteSetting,
    AboutUs, AboutUsMissons, AboutUsValues, AboutUsStats,
    AboutUsTeam, AboutUsQuestions, Gallery
)
from unfold.admin import ModelAdmin as UnfoldModelAdmin

# ==================== CUSTOM ADMIN ACTIONS ====================
def make_published(modeladmin, request, queryset):
    queryset.update(is_active=True)
make_published.short_description = "Tanlanganlarni faollashtirish"

def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_active=False)
make_unpublished.short_description = "Tanlanganlarni faolsizlashtirish"

# ==================== HOME SLIDER ADMIN ====================
@admin.register(HomeSlider)
class HomeSliderAdmin(UnfoldModelAdmin):
    list_display = ('title', 'slider_type', 'order', 'is_active', 'created_at')
    list_display_links = ('title', )
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'slider_type', 'created_at')
    search_fields = ('title', 'description', 'button_text')
    list_per_page = 20
    ordering = ('order', '-created_at')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'preview_media', 'get_media_url_display')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'description', 'button_text', 'button_url')
        }),
        ('Media Kontent', {
            'fields': ('slider_type', 'image', 'video', 'video_url', 'preview_media'),
            'description': 'Slider turini tanlang, keyin mos media ni yuklang'
        }),
        ('Ko\'rinish sozlamalari', {
            'fields': ('order', 'is_active')
        }),
        ('Vaqt yorliqlari', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def display_media_preview(self, obj):
        if obj.slider_type == 'image' and obj.image:
            return format_html(
                '<img src="{}" width="80" height="45" style="border-radius:4px;object-fit:cover;" />',
                obj.image.url
            )
        elif obj.slider_type == 'video':
            if obj.video:
                return format_html(
                    '<div style="width:80px;height:45px;background:#60d5f4;border-radius:4px;display:flex;align-items:center;justify-content:center;color:white;">'
                    '<i class="fas fa-video" style="font-size:20px;"></i>'
                    '</div>'
                )
            elif obj.video_url:
                return format_html(
                    '<div style="width:80px;height:45px;background:#ff4444;border-radius:4px;display:flex;align-items:center;justify-content:center;color:white;">'
                    '<i class="fab fa-youtube" style="font-size:20px;"></i>'
                    '</div>'
                )
        return format_html('<span style="color:#999;">{}</span>', '—')
    display_media_preview.short_description = 'Media'
    
    def preview_media(self, obj):
        if obj.pk:
            if obj.slider_type == 'image' and obj.image:
                return format_html(
                    '<h4>Rasm ko\'rinishi:</h4>'
                    '<img src="{}" width="400" style="border-radius:8px;margin:10px 0;max-width:100%;" />',
                    obj.image.url
                )
            elif obj.slider_type == 'video':
                if obj.video:
                    return format_html(
                        '<h4>Video fayl:</h4>'
                        '<div style="background:#333;color:white;padding:15px;border-radius:8px;margin:10px 0;">'
                        '<i class="fas fa-video" style="margin-right:10px;"></i>{}'
                        '</div>',
                        obj.video.name.split('/')[-1] if obj.video else ''
                    )
                elif obj.video_url:
                    return format_html(
                        '<h4>Video URL:</h4>'
                        '<div style="background:#333;color:white;padding:15px;border-radius:8px;margin:10px 0;">'
                        '<i class="fab fa-youtube" style="margin-right:10px;color:#ff4444;"></i>{}'
                        '</div>',
                        obj.video_url
                    )
        return "Media yuklanmagan yoki tanlanmagan"
    preview_media.short_description = 'Media ko\'rinishi'
    
    def get_media_url_display(self, obj):
        if obj.pk:
            media_url = obj.get_media_url()
            if media_url:
                return format_html(
                    '<strong>Media manzili:</strong><br>'
                    '<code style="background:#f5f5f5;padding:5px;border-radius:3px;display:inline-block;margin-top:5px;">{}</code>',
                    media_url
                )
        return "Media manzili mavjud emas"
    get_media_url_display.short_description = 'Media URL'
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', '-created_at')
    
    actions = ['activate_sliders', 'deactivate_sliders', 'set_as_images', 'set_as_videos']
    
    def activate_sliders(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} ta slider faollashtirildi")
    activate_sliders.short_description = "Tanlangan sliderlarni faollashtirish"
    
    def deactivate_sliders(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} ta slider nofaollashtirildi")
    deactivate_sliders.short_description = "Tanlangan sliderlarni nofaollashtirish"
    
    def set_as_images(self, request, queryset):
        updated = queryset.update(slider_type='image')
        self.message_user(request, f"{updated} ta slider rasm turiga o'zgartirildi")
    set_as_images.short_description = "Rasm turiga o'zgartirish"
    
    def set_as_videos(self, request, queryset):
        updated = queryset.update(slider_type='video')
        self.message_user(request, f"{updated} ta slider video turiga o'zgartirildi")
    set_as_videos.short_description = "Video turiga o'zgartirish"
    
    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = HomeSlider.objects.get(pk=obj.pk)
                if old_obj.slider_type != obj.slider_type:
                    if obj.slider_type == 'image':
                        obj.video = None
                        obj.video_url = ''
                    else:
                        obj.image = None
            except HomeSlider.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)
    
    def clean(self):
        cleaned_data = super().clean()
        slider_type = cleaned_data.get('slider_type')
        
        if slider_type == 'image' and not cleaned_data.get('image'):
            raise ValidationError("Rasm slideri uchun rasm yuklashingiz kerak")
        
        if slider_type == 'video' and not cleaned_data.get('video') and not cleaned_data.get('video_url'):
            raise ValidationError("Video slideri uchun video fayl yoki video URL kiriting")
        
        return cleaned_data

# ==================== SERVICE ADMIN ====================
@admin.register(Service)
class ServiceAdmin(UnfoldModelAdmin):
    list_display = ('title', 'icon_preview', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('title', 'description')
    list_filter = ('is_active', 'created_at')
    list_per_page = 20
    
    fieldsets = (
        ('Xizmat ma\'lumotlari', {
            'fields': ('icon', 'title', 'description')
        }),
        ('Sozlamalar', {
            'fields': ('display_order', 'is_active')
        })
    )
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{} fa-lg"></i> {}', obj.icon, obj.icon)
        return "Icon yo'q"
    icon_preview.short_description = 'Icon'

# ==================== TESTIMONIAL ADMIN ====================
@admin.register(Testimonial)
class TestimonialAdmin(UnfoldModelAdmin):
    list_display = ('full_name', 'region', 'rating_stars', 'created_at', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('rate', 'region', 'is_active', 'created_at')
    search_fields = ('full_name', 'feedback', 'region')
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Mijoz ma\'lumotlari', {
            'fields': ('full_name', 'region', 'rate', 'feedback')
        }),
        ('Sozlamalar', {
            'fields': ('is_active',)
        }),
        ('Vaqt yorliqlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rate + '☆' * (5 - obj.rate)
        return format_html('<span style="color:#ffc107;font-size:16px;">{}</span>', stars)
    rating_stars.short_description = 'Baholash'

# ==================== SITE SETTING ADMIN ====================
@admin.register(SiteSetting)
class SiteSettingAdmin(UnfoldModelAdmin):
    list_display = ('title', 'logo_preview', 'phone_number', 'email', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Sayt asosiy ma\'lumotlari', {
            'fields': ('title', 'logo', 'description')
        }),
        ('Aloqa ma\'lumotlari', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Ijtimoiy tarmoqlar', {
            'fields': ('facebook_url', 'telegram_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Vaqt yorliqlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%;" />', obj.logo.url)
        return "Logo yo'q"
    logo_preview.short_description = 'Logo'
    
    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

# ==================== ABOUT US ADMIN ====================
@admin.register(AboutUs)
class AboutUsAdmin(UnfoldModelAdmin):
    list_display = ('aboutUsTitle', 'image_preview', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Biz haqimizda ma\'lumotlari', {
            'fields': ('aboutUsImage', 'aboutUsTitle', 'aboutUsDescription')
        }),
        ('Vaqt yorliqlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        if obj.aboutUsImage:
            return format_html('<img src="{}" width="80" height="60" style="border-radius:5px;" />', obj.aboutUsImage.url)
        return "Rasm yo'q"
    image_preview.short_description = 'Rasm'
    
    def has_add_permission(self, request):
        return not AboutUs.objects.exists()

# ==================== ABOUT US MISSIONS ADMIN ====================
@admin.register(AboutUsMissons)
class AboutUsMissonsAdmin(UnfoldModelAdmin):
    list_display = ('missionTitle', 'icon_preview', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('missionTitle', 'missionDescription')
    list_filter = ('is_active', 'created_at')
    list_per_page = 20
    
    fieldsets = (
        ('Maqsad ma\'lumotlari', {
            'fields': ('missionIcon', 'missionTitle', 'missionDescription')
        }),
        ('Sozlamalar', {
            'fields': ('display_order', 'is_active')
        })
    )
    
    def icon_preview(self, obj):
        if obj.missionIcon:
            return format_html('<i class="{} fa-lg"></i>', obj.missionIcon)
        return "Icon yo'q"
    icon_preview.short_description = 'Icon'

# ==================== ABOUT US VALUES ADMIN ====================
@admin.register(AboutUsValues)
class AboutUsValuesAdmin(UnfoldModelAdmin):
    list_display = ('valueTitle', 'icon_preview', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('valueTitle', 'valueDescription')
    list_filter = ('is_active', 'created_at')
    list_per_page = 20
    
    fieldsets = (
        ('Qadriyat ma\'lumotlari', {
            'fields': ('valueIcon', 'valueTitle', 'valueDescription')
        }),
        ('Sozlamalar', {
            'fields': ('display_order', 'is_active')
        })
    )
    
    def icon_preview(self, obj):
        if obj.valueIcon:
            return format_html('<i class="{} fa-lg"></i>', obj.valueIcon)
        return "Icon yo'q"
    icon_preview.short_description = 'Icon'

# ==================== ABOUT US STATS ADMIN ====================
@admin.register(AboutUsStats)
class AboutUsStatsAdmin(UnfoldModelAdmin):
    list_display = ('statTitle', 'statValue', 'display_order', 'is_active')
    list_editable = ('statValue', 'display_order', 'is_active')
    search_fields = ('statTitle',)
    list_filter = ('is_active', 'created_at')
    list_per_page = 20
    
    fieldsets = (
        ('Statistika ma\'lumotlari', {
            'fields': ('statTitle', 'statValue')
        }),
        ('Sozlamalar', {
            'fields': ('display_order', 'is_active')
        })
    )

# ==================== ABOUT US TEAM ADMIN ====================
@admin.register(AboutUsTeam)
class AboutUsTeamAdmin(UnfoldModelAdmin):
    list_display = ('teamFullName', 'image_preview', 'teamPosition', 'display_order', 'is_active')
    list_editable = ('teamPosition', 'display_order', 'is_active')
    search_fields = ('teamFullName', 'teamPosition')
    list_filter = ('is_active', 'created_at')
    list_per_page = 20
    
    fieldsets = (
        ('Jamoa a\'zosi ma\'lumotlari', {
            'fields': ('teamImage', 'teamFullName', 'teamPosition')
        }),
        ('Sozlamalar', {
            'fields': ('display_order', 'is_active')
        })
    )
    
    def image_preview(self, obj):
        if obj.teamImage:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;object-fit:cover;" />', obj.teamImage.url)
        return "Rasm yo'q"
    image_preview.short_description = 'Rasm'

# ==================== ABOUT US QUESTIONS ADMIN ====================
@admin.register(AboutUsQuestions)
class AboutUsQuestionsAdmin(UnfoldModelAdmin):
    list_display = ('questionTitle', 'display_order', 'is_active', 'created_at')
    list_editable = ('display_order', 'is_active')
    search_fields = ('questionTitle', 'questionAnswer')
    list_filter = ('is_active', 'created_at')
    list_per_page = 20
    
    fieldsets = (
        ('Savol-Javob ma\'lumotlari', {
            'fields': ('questionTitle', 'questionAnswer')
        }),
        ('Sozlamalar', {
            'fields': ('display_order', 'is_active')
        })
    )

# ==================== GALLERY ADMIN ====================
@admin.register(Gallery)
class GalleryAdmin(UnfoldModelAdmin):
    list_display = ('title', 'media_type', 'category', 'media_preview', 'display_order', 'is_active', 'created_at')
    list_editable = ('display_order', 'is_active')
    list_filter = ('is_active', 'media_type', 'category', 'created_at')
    search_fields = ('title', 'description', 'category')
    list_per_page = 20
    ordering = ('display_order', '-created_at')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at', 'preview_media', 'get_media_url_display')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'description', 'category')
        }),
        ('Media Kontent', {
            'fields': ('media_type', 'image', 'video', 'video_url', 'preview_media'),
            'description': 'Media turini tanlang, keyin mos media ni yuklang'
        }),
        ('Ko\'rinish sozlamalari', {
            'fields': ('display_order', 'is_active')
        }),
        ('Vaqt yorliqlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def media_preview(self, obj):
        if obj.media_type == 'image' and obj.image:
            return format_html(
                '<img src="{}" width="80" height="45" style="border-radius:4px;object-fit:cover;" />',
                obj.image.url
            )
        elif obj.media_type == 'video':
            if obj.video:
                return format_html(
                    '<div style="width:80px;height:45px;background:#60d5f4;border-radius:4px;display:flex;align-items:center;justify-content:center;color:white;">'
                    '<i class="fas fa-video" style="font-size:20px;"></i>'
                    '</div>'
                )
            elif obj.video_url:
                return format_html(
                    '<div style="width:80px;height:45px;background:#ff4444;border-radius:4px;display:flex;align-items:center;justify-content:center;color:white;">'
                    '<i class="fab fa-youtube" style="font-size:20px;"></i>'
                    '</div>'
                )
        return format_html('<span style="color:#999;">{}</span>', '—')
    media_preview.short_description = 'Media'
    
    def preview_media(self, obj):
        if obj.pk:
            if obj.media_type == 'image' and obj.image:
                return format_html(
                    '<h4>Rasm ko\'rinishi:</h4>'
                    '<img src="{}" width="400" style="border-radius:8px;margin:10px 0;max-width:100%;" />',
                    obj.image.url
                )
            elif obj.media_type == 'video':
                if obj.video:
                    return format_html(
                        '<h4>Video fayl:</h4>'
                        '<div style="background:#333;color:white;padding:15px;border-radius:8px;margin:10px 0;">'
                        '<i class="fas fa-video" style="margin-right:10px;"></i>{}'
                        '</div>',
                        obj.video.name.split('/')[-1] if obj.video else ''
                    )
                elif obj.video_url:
                    return format_html(
                        '<h4>Video URL:</h4>'
                        '<div style="background:#333;color:white;padding:15px;border-radius:8px;margin:10px 0;">'
                        '<i class="fab fa-youtube" style="margin-right:10px;color:#ff4444;"></i>{}'
                        '</div>',
                        obj.video_url
                    )
        return "Media yuklanmagan yoki tanlanmagan"
    preview_media.short_description = 'Media ko\'rinishi'
    
    def get_media_url_display(self, obj):
        if obj.pk:
            media_url = obj.get_media_url()
            if media_url:
                return format_html(
                    '<strong>Media manzili:</strong><br>'
                    '<code style="background:#f5f5f5;padding:5px;border-radius:3px;display:inline-block;margin-top:5px;">{}</code>',
                    media_url
                )
        return "Media manzili mavjud emas"
    get_media_url_display.short_description = 'Media URL'
    
    actions = [make_published, make_unpublished]
    
    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_obj = Gallery.objects.get(pk=obj.pk)
                if old_obj.media_type != obj.media_type:
                    if obj.media_type == 'image':
                        obj.video = None
                        obj.video_url = ''
                    else:
                        obj.image = None
            except Gallery.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)