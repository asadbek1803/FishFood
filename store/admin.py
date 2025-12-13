# store/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from decimal import Decimal
from .models import Category, Product, Order, Courier, CourierToken
from unfold.admin import ModelAdmin as UnfoldModelAdmin

# ==================== CATEGORY ADMIN ====================
@admin.register(Category)
class CategoryAdmin(UnfoldModelAdmin):
    list_display = ('name', 'display_product_count', 'get_created_at_display', 'get_is_active_display')
    list_editable = ()
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'created_at')
    list_per_page = 20
    
    fieldsets = (
        ('Kategoriya ma\'lumotlari', {
            'fields': ('name', 'description')
        }),
        ('Sozlamalar', {
            'fields': ('display_order', 'is_active')
        })
    )
    
    def display_product_count(self, obj):
        count = obj.products.count()
        return format_html('<span style="background:#60D5F4;color:#2C2940;padding:2px 8px;border-radius:10px;">{}</span>', count)
    display_product_count.short_description = 'Mahsulotlar'
    display_product_count.admin_order_field = 'products'
    
    def get_created_at_display(self, obj):
        return obj.created_at.strftime('%d.%m.%Y')
    get_created_at_display.short_description = 'Yaratilgan sana'
    get_created_at_display.admin_order_field = 'created_at'
    
    def get_is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;">{}</span>', '✅')
        return format_html('<span style="color:red;">{}</span>', '❌')
    get_is_active_display.short_description = 'Holati'

# ==================== PRODUCT ADMIN ====================
# ==================== PRODUCT ADMIN ====================
@admin.register(Product)
class ProductAdmin(UnfoldModelAdmin):
    # Remove 'display_image' from list_display_links since it's not a real field
    list_display = ('display_image', 'name', 'category', 'display_price', 'old_price', 'display_stock', 'display_discount', 'get_is_active_display')
    list_display_links = ('name',)  # Changed from ('display_image', 'name')
    list_editable = ()
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_per_page = 20
    
    # Add this to prevent Django from trying to order by display_image
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')
    
    fieldsets = (
        ('Asosiy ma\'lumotlari', {
            'fields': ('category', 'name', 'description')
        }),
        ('Narx va miqdor', {
            'fields': ('price', 'stock', 'old_price')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Sozlamalar', {
            'fields': ('display_order', 'is_active')
        })
    )
    
    def display_image(self, obj):
        if not obj.image:
            return mark_safe(
                '<div style="width:50px;height:50px;background:#2C2940;border-radius:5px;'
                'display:flex;align-items:center;justify-content:center;">'
                '<i class="fas fa-fish" style="color:#60D5F4;"></i>'
                '</div>'
            )
        
        try:
            # Make sure image.url exists
            url = obj.image.url
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:5px;object-fit:cover;" />',
                url
            )
        except (AttributeError, ValueError):
            # Handle case where image exists but url doesn't
            return mark_safe(
                '<div style="width:50px;height:50px;background:#2C2940;border-radius:5px;'
                'display:flex;align-items:center;justify-content:center;">'
                '<i class="fas fa-image" style="color:#60D5F4;"></i>'
                '</div>'
            )
    display_image.short_description = 'Rasm'
    # Add this to prevent Django from trying to order by this method
    display_image.admin_order_field = None
    
    def display_price(self, obj):
        price_int = int(obj.price)
        return format_html('{}', price_int)
    display_price.short_description = 'Narxi'
    display_price.admin_order_field = 'price'
    
    def display_stock(self, obj):
        if obj.stock:
            stock_int = int(obj.stock)
            price_int = int(obj.price)
            if price_int > stock_int:
                return format_html('{}', stock_int)
            return format_html('{}', stock_int)
        return format_html('<span style="color:#999;">{}</span>', '-')
    display_stock.short_description = 'Aksiya narxi'
    display_stock.admin_order_field = 'stock'
    
    def display_discount(self, obj):
        discount = obj.get_price_action_percent()
        if discount > 0:
            discount_formatted = "{:.0f}".format(discount)
            return format_html(
                '<span style="background:#ff4444;color:white;padding:2px 8px;border-radius:10px;">{}%</span>',
                discount_formatted
            )
        return format_html('<span style="color:#999;">{}</span>', '-')
    display_discount.short_description = 'Chegirma'
    display_discount.admin_order_field = None
    
    def get_is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color:green;">{}</span>', '✅')
        return format_html('<span style="color:red;">{}</span>', '❌')
    get_is_active_display.short_description = 'Holati'
    get_is_active_display.admin_order_field = 'is_active'
    
    def get_created_at_display(self, obj):
        return obj.created_at.strftime('%d.%m.%Y')
    get_created_at_display.short_description = 'Yaratilgan sana'
    
    def save_model(self, request, obj, form, change):
        if not obj.stock:
            obj.stock = obj.price
        super().save_model(request, obj, form, change)

# ==================== CUSTOM ADMIN ACTIONS ====================
@admin.action(description="Tanlanganlarni faollashtirish")
def make_active(_, request, queryset):
    queryset.update(is_active=True)

@admin.action(description="Tanlanganlarni faolsizlashtirish")
def make_inactive(_, request, queryset):
    queryset.update(is_active=False)


@admin.register(Order)
class OrderAdmin(UnfoldModelAdmin):
    list_display = ('order_id', 'full_name_display', 'status', 'total_price_display', 'status_display', 'payment_method_display', 'created_at_display')
    list_filter = ('status', 'payment_method', 'region', 'created_at')
    search_fields = ('order_id', 'full_name', 'phone', 'address')
    readonly_fields = ('order_id', 'created_at')
    list_editable = ('status',)
    actions = ['mark_as_completed', 'mark_as_processing', 'export_orders']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'status', 'total_price', 'created_at')
        }),
        ('Customer Information', {
            'fields': ('full_name', 'phone', 'region', 'district', 'address')
        }),
        ('Order Details', {
            'fields': ('products', 'payment_method', 'comments'),
        }),
    )
    
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Customer'
    
    def total_price_display(self, obj):
        return f"${obj.total_price}"
    total_price_display.short_description = 'Total'
    
    def status_display(self, obj):
        status_colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'canceled': 'red',
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def payment_method_display(self, obj):
        return obj.get_payment_method_display()
    payment_method_display.short_description = 'Payment'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime("%b %d, %Y %H:%M")
    created_at_display.short_description = 'Date'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} orders marked as completed.')
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    
    def export_orders(self, request, queryset):
        pass
    
    mark_as_completed.short_description = "Mark selected orders as completed"
    mark_as_processing.short_description = "Mark selected orders as processing"
    export_orders.short_description = "Export selected orders"


@admin.register(Courier)
class CourierAdmin(UnfoldModelAdmin):
    list_display = ['full_name', 'phone', 'region', 'status', 'total_orders', 'success_rate', 'created_at']
    list_filter = ['status', 'region', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'telegram_username']
    readonly_fields = ['telegram_id', 'total_orders', 'completed_orders', 'cancelled_orders', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'phone', 'region')
        }),
        ('Telegram', {
            'fields': ('telegram_id', 'telegram_username')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Statistika', {
            'fields': ('total_orders', 'completed_orders', 'cancelled_orders')
        }),
        ('Sanalar', {
            'fields': ('created_at', 'updated_at', 'last_active')
        }),
    )
    
    def success_rate(self, obj):
        return f"{obj.success_rate}%"
    success_rate.short_description = 'Muvaffaqiyat %'


@admin.register(CourierToken)
class CourierTokenAdmin(UnfoldModelAdmin):
    list_display = ['token_short', 'is_used', 'created_by', 'used_by', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['token', 'created_by__username']
    readonly_fields = ['token', 'created_by', 'created_at', 'used_at', 'used_by']
    
    def token_short(self, obj):
        return f"{obj.token[:20]}..."
    token_short.short_description = 'Token'
    
    def has_add_permission(self, request):
        return False

# Admin actionlarni qo'shamiz
CategoryAdmin.actions = [make_active, make_inactive]