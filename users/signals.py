from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for every new User."""
    if created:
        request = kwargs.get('request')
        if request and hasattr(request, '_birth_date') and hasattr(request, '_gender'):
            UserProfile.objects.create(
                user=instance,
                birth_date=request._birth_date,
                gender=request._gender,
                height=170.0,
                career='Not specified',
                income=0.0,
                contact_info='',
                preferred_gender='Both',
                preferred_age_min=18,
                preferred_age_max=100,
                preferred_distance=50,
            )
        else:
            UserProfile.objects.create(
                user=instance,
                gender='Other',
                height=170.0,
                career='Not specified',
                income=0.0,
                contact_info='',
                preferred_gender='Both',
                preferred_age_min=18,
                preferred_age_max=100,
                preferred_distance=50,
            )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile whenever the User is saved."""
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(
            user=instance,
            gender='Other',
            height=170.0,
            career='Not specified',
            income=0.0,
            contact_info='',
            preferred_gender='Both',
            preferred_age_min=18,
            preferred_age_max=100,
            preferred_distance=50,
        )
