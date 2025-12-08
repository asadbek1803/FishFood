
from django.shortcuts import render
from django.http import JsonResponse
from store.models import Order
from store.models import Product
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import TruncMonth, ExtractHour, ExtractWeekDay
from datetime import datetime, timedelta
import json
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def dashboard(request):
    # Filter
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    region = request.GET.get("region")

    orders = Order.objects.all()

    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)

    if end_date:
        orders = orders.filter(created_at__date__lte=end_date)

    if region:
        orders = orders.filter(region=region)

    # Buyurtma statuslari
    status_stats = orders.values("status").annotate(count=Count("id"))

    # Viloyatlar bo‘yicha statistika
    region_stats = orders.values("region").annotate(count=Count("id")).order_by("-count")

    # Mahsulotlar statistikasi
    product_stats = (
        Order.objects.values("products__name")
        .annotate(count=Count("products"))
        .order_by("-count")[:10]
    )

    # Oylik daromad
    monthly_income = (
        orders.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total_price"))
        .order_by("month")
    )

    context = {
        "registered_count": 532,  # misol
        "paid_count": 312,        # misol
        "unpaid_count": 220,      # misol

        "status_stats": list(status_stats),
        "region_stats": list(region_stats),
        "product_stats": list(product_stats),
        "monthly_income": list(monthly_income),
    }
    return render(request, "admin/index.html", context)


@staff_member_required
def dashboard_api(request):
    """API endpoint for dashboard data"""
    period = request.GET.get('period', 'week')
    
    # Calculate date range
    today = datetime.now().date()
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=7)
    
    # Get data
    orders = Order.objects.filter(created_at__date__gte=start_date)
    
    # Daily sales
    daily_sales = (
        orders.values('created_at__date')
        .annotate(
            revenue=Sum('total_price'),
            orders=Count('id'),
            avg_order=Sum('total_price')/Count('id')
        )
        .order_by('created_at__date')
    )
    
    # Top products
    top_products = (
        Product.objects.annotate(
            sold=Count('order', distinct=True),
            revenue=Sum('order__total_price', distinct=True),
        )
        .filter(sold__gt=0)
        .order_by('-sold')[:10]
        .values('id', 'name', 'sold', 'revenue')
    )

    
    # Status distribution
    status_stats = (
        orders.values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Payment methods
    payment_stats = (
        orders.values('payment_method')
        .annotate(count=Count('id'), total=Sum('total_price'))
        .order_by('-count')
    )
    
    # Customer acquisition
    new_customers = (
        User.objects.filter(date_joined__date__gte=start_date)
        .values('date_joined__date')
        .annotate(count=Count('id'))
        .order_by('date_joined__date')
    )
    
    return JsonResponse({
        'daily_sales': list(daily_sales),
        'top_products': list(top_products),
        'status_stats': list(status_stats),
        'payment_stats': list(payment_stats),
        'new_customers': list(new_customers),
    })

@staff_member_required
def export_report(request):
    """Export report data"""
    report_type = request.GET.get('type', 'sales')
    format_type = request.GET.get('format', 'csv')
    
    # Generate report data based on type
    if report_type == 'sales':
        data = Order.objects.all().values()
    elif report_type == 'products':
        data = Product.objects.all().values()
    elif report_type == 'customers':
        data = User.objects.all().values()
    
    # Convert to requested format (simplified)
    if format_type == 'csv':
        # Generate CSV
        pass
    elif format_type == 'json':
        return JsonResponse({'data': list(data)})
    elif format_type == 'excel':
        # Generate Excel
        pass
    
    return JsonResponse({'status': 'Export not implemented'})

@staff_member_required
def realtime_stats(request):
    """Get real-time statistics"""
    today = datetime.now().date()
    
    # Real-time data
    stats = {
        'today_orders': Order.objects.filter(created_at__date=today).count(),
        'today_revenue': Order.objects.filter(created_at__date=today).aggregate(Sum('total_price'))['total_price__sum'] or 0,
        'pending_orders': Order.objects.filter(status='pending').count(),
        'low_stock': Product.objects.filter(stock__lt=10).count(),
        'new_customers_today': User.objects.filter(date_joined__date=today).count(),
    }
    
    return JsonResponse(stats)