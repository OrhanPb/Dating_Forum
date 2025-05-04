from django.utils.timezone import now
from users.models import UserProfile
from datetime import timedelta
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.contrib.auth.models import User

class OnlineStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = now()
            try:
                profile = request.user.userprofile
                if 'user_location' in request.session:
                    location = request.session['user_location']
                    profile.latitude = location.get('latitude')
                    profile.longitude = location.get('longitude')
                
                profile.last_seen = current_time
                profile.is_online = True
                profile.save(update_fields=['is_online', 'last_seen', 'latitude', 'longitude'])
            except UserProfile.DoesNotExist:
                pass

        cutoff_time = now() - timedelta(minutes=5)
        
        valid_sessions = Session.objects.filter(expire_date__gt=now())
        active_user_ids = set()
        
        for session in valid_sessions:
            try:
                user_id = session.get_decoded().get('_auth_user_id')
                if user_id:
                    active_user_ids.add(int(user_id))
            except:
                continue
        
        UserProfile.objects.filter(
            Q(last_seen__lt=cutoff_time) |
            ~Q(user_id__in=active_user_ids),
            is_online=True
        ).update(
            is_online=False,
            last_seen=now()
        )

        response = self.get_response(request)
        return response

    def process_request(self, request):
        if request.user.is_authenticated:
            cutoff_time = now() - timedelta(minutes=5)
            UserProfile.objects.filter(
                last_seen__lt=cutoff_time,
                is_online=True
            ).update(is_online=False)
