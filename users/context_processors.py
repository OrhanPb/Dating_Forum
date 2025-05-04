from .models import UserProfile
from django.conf import settings

def user_profile(request):
    """Add user profile to the template context if it exists."""
    if request.user.is_authenticated:
        try:
            return {'user_profile': request.user.userprofile}
        except UserProfile.DoesNotExist:
            return {'user_profile': None}
    return {'user_profile': None}

def google_maps_api_key(request):
    """Add Google Maps API key to the template context."""
    return {'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY} 