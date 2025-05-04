from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.utils.functional import SimpleLazyObject
from datetime import date, timedelta
from django.utils import timezone

class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Other')
    height = models.FloatField(default=170.0)
    career = models.CharField(max_length=100, default='Not specified')
    income = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    contact_info = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=now)
    
    bio = models.TextField(max_length=500, blank=True)
    interests = models.ManyToManyField('Interest', blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    last_activity = models.DateTimeField(default=now)
    location_name = models.CharField(max_length=255, blank=True)
    
    preferred_gender = models.CharField(
        max_length=10, 
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Both', 'Both')], 
        default='Both'
    )
    preferred_age_min = models.IntegerField(default=18)
    preferred_age_max = models.IntegerField(default=100)
    preferred_distance = models.IntegerField(default=50, help_text='Maximum distance in kilometers')
    looking_for = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Both', 'Both')], default='Both')
    
    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_matching_profiles(self):
        from django.db.models import Q
        
        today = date.today()
        min_birth_date = date(today.year - self.preferred_age_max - 1, today.month, today.day)
        max_birth_date = date(today.year - self.preferred_age_min, today.month, today.day)
        
        matches = UserProfile.objects.filter(
            Q(gender=self.preferred_gender) | Q(preferred_gender='Both')
        ).filter(
            birth_date__gte=min_birth_date,
            birth_date__lte=max_birth_date
        ).exclude(user=self.user)
        
        return matches

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    def __str__(self):
        return self.title

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    is_mutual = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f'Match between {self.user1.username} and {self.user2.username}'

    def get_other_user_for_match(self):
        request_user = getattr(self, '_request_user', None)
        if request_user == self.user1:
            return self.user2
        return self.user1

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dating_sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dating_received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

    @staticmethod
    def get_unread_count(user):
        return ChatMessage.objects.filter(receiver=user, is_read=False).count()

    @staticmethod
    def get_messages_between_users(user1, user2):
        return ChatMessage.objects.filter(
            (models.Q(sender=user1, receiver=user2) |
             models.Q(sender=user2, receiver=user1))
        ).order_by('timestamp')
