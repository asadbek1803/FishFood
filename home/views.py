from django.shortcuts import render
from home.models import HomeSlider, Service, AboutUsQuestions, Testimonial,AboutUsTeam, SiteSetting, AboutUs, AboutUsMissons, AboutUsValues, AboutUsStats, Gallery
from store.models import Product
# Create your views here.

def home_view(request):
    data = {
        'sliders': HomeSlider.objects.all(),
        'services': Service.objects.all(),
        'public_products': Product.objects.all()[:8],
        'testimonials': Testimonial.objects.all(),
        'site_settings': SiteSetting.objects.first(),
        'about_us': AboutUs.objects.first(),
        'about_us_missions': AboutUsMissons.objects.all(),
    }
    return render(request, 'index.html', context=data)

def about_view(request):
    data = {
        'site_settings': SiteSetting.objects.first(),
        'about_us': AboutUs.objects.first(),
        'about_us_missions': AboutUsMissons.objects.all(),
        'about_us_values': AboutUsValues.objects.all(),
        'about_us_stats': AboutUsStats.objects.all(),
        'about_us_team': AboutUsTeam.objects.all(),
        'about_us_questions': AboutUsQuestions.objects.all(),
    }
    return render(request, 'about.html', context=data)

def gallery_view(request):
    galleries = Gallery.objects.filter(is_active=True)
    
    # Kategoriyalar bo'yicha guruhlash
    categories = galleries.values_list('category', flat=True).distinct().exclude(category__isnull=True).exclude(category='')
    
    # Tanlangan kategoriya
    selected_category = request.GET.get('category', 'all')
    
    if selected_category != 'all':
        galleries = galleries.filter(category=selected_category)
    
    data = {
        'galleries': galleries,
        'categories': categories,
        'selected_category': selected_category,
        'site_settings': SiteSetting.objects.first(),
    }
    return render(request, 'gallery.html', context=data)