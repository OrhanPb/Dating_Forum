from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, BlogPost, Match

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_age')
    
    def get_age(self, obj):
        try:
            return obj.userprofile.age
        except UserProfile.DoesNotExist:
            return None
    get_age.short_description = 'Age'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'likes_count')
    search_fields = ('title', 'content', 'user__username')
    list_filter = ('created_at',)
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'is_mutual', 'created_at')
    list_filter = ('is_mutual', 'created_at')
    search_fields = ('user1__username', 'user2__username')
