from .models import SiteSetting

def site_settings(request):
    try:
        settings = SiteSetting.objects.first()
        return {'site_settings': settings}
    except SiteSetting.DoesNotExist:
        return {'site_settings': None}
