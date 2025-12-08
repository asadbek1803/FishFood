from django.urls import path
from . import views


urlpatterns = [
    
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
    path('api/realtime/', views.realtime_stats, name='realtime_stats'),
    path('api/export/', views.export_report, name='export_report'),
]   