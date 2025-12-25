from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from home.views import home_view, about_view, gallery_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('gallery/', gallery_view, name='gallery'),
    path('store/', include('store.urls'), name='store'),
    path('dashboard/', include('dashboard.url'), name='dashboard'),
]  

# Static va Media files serving
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production uchun ham media files serving (Railway uchun)
    # /app/ path'ni olib tashlash uchun to'g'ridan-to'g'ri serve qilamiz
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
