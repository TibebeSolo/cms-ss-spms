from .models import SundaySchool

def branding(request):
    """Injects the active Sunday School branding into all templates."""
    # In a multi-tenant setup, you'd filter by request.host or user profile
    ss = SundaySchool.objects.filter(is_active=True).first()
    return {
        'brand': ss,
        'brand_primary': ss.primary_color if ss else "#1e3a8a",
        'brand_secondary': ss.secondary_color if ss else "#fbbf24",
        'brand_logo': ss.primary_logo if ss else None,
        'brand_symbol': ss.symbol_logo if ss else None,
    }