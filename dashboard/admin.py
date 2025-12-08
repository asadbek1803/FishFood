# dashboard/admin.py

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta, datetime
import json


def dashboard_view(request):
    """Custom dashboard view"""
    from store.models import Order, Product
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Filters
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    region = request.GET.get('region', '')
    status = request.GET.get('status', '')

    # Base queryset
    orders = Order.objects.all()
    
    # Apply filters
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=start)
        except:
            start_date = ''
            
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=end)
        except:
            end_date = ''
            
    if region:
        orders = orders.filter(region=region)
        
    if status:
        orders = orders.filter(status=status)

    # Today stats
    today_orders = Order.objects.filter(created_at__date=today)
    today_revenue = today_orders.aggregate(total=Sum('total_price'))['total'] or 0
    today_stats = {
        'orders': today_orders.count(),
        'revenue': float(today_revenue)
    }

    # Overall stats
    total_revenue = orders.aggregate(total=Sum('total_price'))['total'] or 0
    order_count = orders.count()
    completed_count = orders.filter(status='completed').count()
    
    stats = {
        'total_orders': order_count,
        'total_revenue': float(total_revenue),
        'avg_order_value': float(total_revenue / order_count) if order_count > 0 else 0,
        'completed': completed_count
    }

    # User stats
    user_stats = {
        'total': User.objects.count(),
        'today': User.objects.filter(date_joined__date=today).count()
    }

    # Weekly data for chart (last 7 days)
    weekly_data = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        day_orders = Order.objects.filter(created_at__date=date)
        day_revenue = day_orders.aggregate(total=Sum('total_price'))['total'] or 0
        
        weekly_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'orders': day_orders.count(),
            'revenue': float(day_revenue)
        })

    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]

    # Low stock products
    low_stock = Product.objects.filter(stock__lt=15).order_by('stock')[:5]

    # Top products by revenue
    top_products = []
    try:
        top_items = Order.objects.values('product__name')\
            .annotate(
                total_sold=Sum('quantity'),
                total_revenue=Sum('price')
            )\
            .order_by('-total_revenue')[:10]
        
        for item in top_items:
            top_products.append({
                'products__name': item['product__name'],
                'total_sold': item['total_sold'],
                'total_revenue': float(item['total_revenue'] or 0)
            })
    except:
        for product in Product.objects.all()[:10]:
            top_products.append({
                'products__name': product.name,
                'total_sold': 0,
                'total_revenue': 0.0
            })

    # Region choices for filter (faqat viloyatlar)
    region_list = (
        Order.objects
        .exclude(Q(region__isnull=True) | Q(region__exact=''))
        .values_list('region', flat=True)
    )

    # Unique + sorted format: [('Fargona', 'Fargona'), ...]
    region_choices = [(r, r) for r in sorted(set(region_list))]

    # Status choices
    try:
        status_choices = Order.STATUS_CHOICES
    except:
        status_choices = [
            ('pending', 'Kutilmoqda'),
            ('processing', 'Jarayonda'),
            ('completed', 'Yetkazilgan'),
            ('cancelled', 'Bekor qilingan'),
        ]

    context = {
        'site_title': 'Sea FoodISH',
        'site_header': 'Sea FoodISH Admin',
        'title': 'Dashboard',
        'today_stats': today_stats,
        'stats': stats,
        'user_stats': user_stats,
        'weekly_data': json.dumps(weekly_data),
        'recent_orders': recent_orders,
        'low_stock': low_stock,
        'top_products': top_products,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'region': region,
            'status': status
        },
        'region_choices': region_choices,
        'status_choices': status_choices,
    }
    
    return render(request, 'admin/dashboard.html', context)


# Unfold admin panelini saqlab qolamiz
admin.site.site_header = "Sea FoodISH Admin"
admin.site.site_title = "Sea FoodISH"
admin.site.index_title = "Boshqaruv paneli"

# Dashboard URL ni admin site ga qo'shamiz
from django.contrib.admin import site as admin_site_original

# URL pattern qo'shish uchun
original_get_urls = admin.site.get_urls

def custom_get_urls():
    urls = original_get_urls()
    from django.urls import path
    custom_urls = [
        path('dashboard/', admin.site.admin_view(dashboard_view), name='custom_dashboard'),
    ]
    return custom_urls + urls

admin.site.get_urls = custom_get_urls