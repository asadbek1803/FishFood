from .models import SiteSetting, SEOMetadata

def site_settings(request):
    try:
        settings = SiteSetting.objects.first()
        return {'site_settings': settings}
    except SiteSetting.DoesNotExist:
        return {'site_settings': None}

def seo_metadata(request):
    """Har bir sahifa uchun SEO metadata'larni qaytaradi"""
    try:
        # URL path bo'yicha sahifa aniqlash
        path = request.path.strip('/')
        page_map = {
            '': 'home',
            'about': 'about',
            'gallery': 'gallery',
            'shop': 'shop',
            'store': 'shop',
            'contact': 'contact',
        }
        
        page = page_map.get(path, None)
        
        if page:
            seo = SEOMetadata.objects.filter(page=page, is_active=True).first()
            if seo:
                return {
                    'seo_metadata': seo,
                    'meta_title': seo.meta_title,
                    'meta_description': seo.meta_description,
                    'meta_keywords': seo.meta_keywords,
                    'robots_meta': seo.robots_meta,
                    'canonical_url': seo.get_canonical_url(request),
                    'og_title': seo.og_title or seo.meta_title,
                    'og_description': seo.og_description or seo.meta_description,
                    'og_image': seo.get_og_image_url(),
                    'og_type': seo.og_type,
                    'twitter_card': seo.twitter_card,
                    'twitter_title': seo.twitter_title or seo.og_title or seo.meta_title,
                    'twitter_description': seo.twitter_description or seo.og_description or seo.meta_description,
                    'twitter_image': seo.get_twitter_image_url(),
                    'structured_data': seo.structured_data,
                    'schema_type': seo.schema_type,
                }
    except Exception:
        pass
    
    # Default values
    return {
        'seo_metadata': None,
        'meta_title': '',
        'meta_description': '',
        'meta_keywords': '',
        'robots_meta': 'index, follow',
        'canonical_url': request.build_absolute_uri(request.path) if request else '',
        'og_title': '',
        'og_description': '',
        'og_image': '',
        'og_type': 'website',
        'twitter_card': 'summary_large_image',
        'twitter_title': '',
        'twitter_description': '',
        'twitter_image': '',
        'structured_data': None,
        'schema_type': None,
    }
