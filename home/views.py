from django.shortcuts import render
from home.models import HomeSlider, Service, AboutUsQuestions, Testimonial,AboutUsTeam, SiteSetting, AboutUs, AboutUsMissons, AboutUsValues, AboutUsStats
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