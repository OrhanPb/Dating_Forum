from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, ProfileForm, BlogPostForm
from .models import BlogPost, UserProfile, Match, ChatMessage
from django.db.models import Q
from math import radians, sin, cos, sqrt, atan2
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import json
from datetime import date
from django.utils.timezone import now

def home(request):
    return render(request, 'users/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'birth_date': form.cleaned_data['birth_date'],
                    'gender': form.cleaned_data['gender'],
                    'height': 170.0,
                    'career': 'Not specified',
                    'income': 0.0,
                    'contact_info': '',
                    'preferred_gender': 'Both',
                    'preferred_age_min': 18,
                    'preferred_age_max': 100,
                    'preferred_distance': 50,
                }
            )
            
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Dating Forum!')
            return redirect('users:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('users:profile')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def user_logout(request):
    # Set user offline before logout
    try:
        profile = request.user.userprofile
        profile.is_online = False
        profile.last_seen = now()
        profile.save(update_fields=['is_online', 'last_seen'])
    except UserProfile.DoesNotExist:
        pass
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:login')

@login_required
def profile(request):
    return render(request, 'users/profile.html')

@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(UserProfile, user_id=pk)
    is_matched = Match.objects.filter(
        (Q(user1=request.user, user2=profile.user) |
         Q(user1=profile.user, user2=request.user)),
        is_mutual=True
    ).exists()
    
    context = {
        'profile': profile,
        'is_matched': is_matched
    }
    return render(request, 'users/profile_detail.html', context)

@login_required
def edit_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def search_matches(request):
    user_profile = request.user.userprofile
    query = request.GET.get('q', '')
    age_min = int(request.GET.get('age_min', user_profile.preferred_age_min))
    age_max = int(request.GET.get('age_max', user_profile.preferred_age_max))
    gender = request.GET.get('gender', user_profile.preferred_gender)
    distance = int(request.GET.get('distance', user_profile.preferred_distance))

    # Calculate birth date range for age filtering
    today = date.today()
    min_birth_date = date(today.year - age_max - 1, today.month, today.day)
    max_birth_date = date(today.year - age_min, today.month, today.day)

    profiles = UserProfile.objects.exclude(user=request.user)

    if gender and gender != 'Both':
        profiles = profiles.filter(gender__iexact=gender)

    # Filter by birth date range only for users who have birth dates
    profiles = profiles.filter(
        Q(birth_date__isnull=True) |
        Q(birth_date__gte=min_birth_date, birth_date__lte=max_birth_date)
    )

    # Filter by distance if user has location
    if user_profile.latitude and user_profile.longitude and distance:
        nearby_profiles = []
        for profile in profiles:
            if profile.latitude and profile.longitude:
                dist = calculate_distance(
                    user_profile.latitude, user_profile.longitude,
                    profile.latitude, profile.longitude
                )
                if dist <= distance:
                    profile.distance = dist
                    nearby_profiles.append(profile)
        profiles = nearby_profiles

    if query:
        profiles = [p for p in profiles if (
            query.lower() in p.user.username.lower() or
            query.lower() in (p.bio or '').lower() or
            any(query.lower() in interest.name.lower() for interest in p.interests.all())
        )]

    context = {
        'profiles': profiles,
        'query': query,
        'age_min': age_min,
        'age_max': age_max,
        'gender': gender,
        'distance': distance
    }
    
    return render(request, 'users/search.html', context)

@login_required
def like_profile(request, user_id):
    if request.method == 'POST':
        liked_user = get_object_or_404(User, id=user_id)
        
        # Check if users already matched
        match = Match.objects.filter(
            (Q(user1=request.user, user2=liked_user) |
             Q(user1=liked_user, user2=request.user))
        ).first()

        if not match:
            # Create new match
            match = Match.objects.create(
                user1=request.user,
                user2=liked_user
            )
            messages.success(request, f'You liked {liked_user.username}\'s profile!')
        
        # Check if it's a mutual match
        reverse_match = Match.objects.filter(
            user1=liked_user,
            user2=request.user
        ).exists()

        if reverse_match and not match.is_mutual:
            match.is_mutual = True
            match.save()
            messages.success(request, f'Congratulations! You and {liked_user.username} have matched!')

    return redirect('users:search')

@login_required
def matches_list(request):
    mutual_matches = Match.objects.filter(
        Q(user1=request.user, is_mutual=True) |
        Q(user2=request.user, is_mutual=True)
    )
    
    # Set request user on each match object
    for match in mutual_matches:
        match._request_user = request.user
        
    context = {
        'matches': mutual_matches
    }
    return render(request, 'users/matches.html', context)

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('users:blog_list')
    else:
        form = BlogPostForm()
    return render(request, 'users/blog_post.html', {'form': form})

@login_required
def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'users/blog_list.html', {'posts': posts})

@login_required
def blog_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    previous_post = BlogPost.objects.filter(created_at__lt=post.created_at).order_by('-created_at').first()
    next_post = BlogPost.objects.filter(created_at__gt=post.created_at).order_by('created_at').first()
    
    context = {
        'post': post,
        'previous_post': previous_post,
        'next_post': next_post,
    }
    return render(request, 'users/blog_detail.html', context)

@login_required
def like_blog_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return JsonResponse({
            'status': 'success',
            'likes': post.likes.count()
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def edit_blog_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.user != post.user:
        messages.error(request, "You don't have permission to edit this post.")
        return redirect('users:blog_detail', post_id=post_id)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('users:blog_detail', post_id=post_id)
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'users/blog_post.html', {'form': form})

def search_profiles(request):
    query = request.GET.get('q', '')
    results = UserProfile.objects.filter(
        Q(gender__iexact=query) | Q(career__icontains=query) | Q(income__gte=query) | Q(age__gte=query)
    )
    return render(request, 'users/search_results.html', {'results': results, 'query': query})

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance

@login_required
def chat_inbox(request):
    # Get all users that the current user has matched with
    matches = Match.objects.filter(
        (Q(user1=request.user) | Q(user2=request.user)),
        is_mutual=True
    )
    
    chat_users = []
    for match in matches:
        other_user = match.user2 if match.user1 == request.user else match.user1
        last_message = ChatMessage.get_messages_between_users(request.user, other_user).last()
        unread_count = ChatMessage.objects.filter(sender=other_user, receiver=request.user, is_read=False).count()
        
        chat_users.append({
            'user': other_user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Sort by last message time, putting unread messages first
    chat_users.sort(key=lambda x: (
        0 if x['unread_count'] > 0 else 1,
        x['last_message'].created_at if x['last_message'] else timezone.now()
    ), reverse=True)
    
    return render(request, 'users/chat_inbox.html', {'chat_users': chat_users})

@login_required
def chat_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if users are matched
    is_matched = Match.objects.filter(
        (Q(user1=request.user, user2=other_user) | Q(user1=other_user, user2=request.user)),
        is_mutual=True
    ).exists()
    
    if not is_matched:
        messages.error(request, "You can only chat with users you've matched with.")
        return redirect('users:matches')
    
    # Get chat messages
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user, receiver=other_user) | 
         Q(sender=other_user, receiver=request.user))
    ).order_by('timestamp')
    
    context = {
        'other_user': other_user,
        'messages': messages,
    }
    
    return render(request, 'users/chat_room.html', context)

@login_required
def send_message(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if users are matched
    is_matched = Match.objects.filter(
        (Q(user1=request.user, user2=other_user) | Q(user1=other_user, user2=request.user)),
        is_mutual=True
    ).exists()
    
    if not is_matched:
        return JsonResponse({'status': 'error', 'message': 'You can only chat with matched users'})
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Message content cannot be empty'})
        
        message = ChatMessage.objects.create(
            sender=request.user,
            receiver=other_user,
            content=content
        )
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%I:%M %p'),
                'is_sender': True
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def get_messages(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    after_id = request.GET.get('after', 0)
    
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user, receiver=other_user) | 
         Q(sender=other_user, receiver=request.user)),
        id__gt=after_id
    ).order_by('timestamp')
    
    return JsonResponse({
        'messages': [{
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%I:%M %p'),
            'is_sender': msg.sender == request.user
        } for msg in messages]
    })

@login_required
def get_unread_count(request):
    count = ChatMessage.get_unread_count(request.user)
    return JsonResponse({'count': count})

@login_required
def map_view(request):
    return render(request, 'users/map_view.html')

@login_required
def map_users_api(request):
    try:
        # Get filter parameters
        distance = float(request.GET.get('distance', 50))
        gender = request.GET.get('gender', 'Both')
        age_min = int(request.GET.get('age_min', 18))
        age_max = int(request.GET.get('age_max', 100))
        
        # Get current user's location
        user_profile = request.user.userprofile
        if not user_profile.latitude or not user_profile.longitude:
            return JsonResponse({
                'error': 'Please update your location in your profile settings.'
            })
        
        # Query users based on filters
        profiles = UserProfile.objects.exclude(user=request.user)
        
        if gender != 'Both':
            profiles = profiles.filter(gender=gender)
        
        # Filter by age
        today = date.today()
        min_date = date(today.year - age_max, today.month, today.day)
        max_date = date(today.year - age_min, today.month, today.day)
        profiles = profiles.filter(birth_date__range=[min_date, max_date])
        
        # Calculate distances and filter
        users_data = []
        for profile in profiles:
            if profile.latitude and profile.longitude:
                # Calculate distance using Haversine formula
                R = 6371  # Earth's radius in kilometers
                lat1, lon1 = radians(user_profile.latitude), radians(user_profile.longitude)
                lat2, lon2 = radians(profile.latitude), radians(profile.longitude)
                
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                d = R * c
                
                if d <= distance:
                    users_data.append({
                        'id': profile.user.id,
                        'username': profile.user.username,
                        'age': profile.age,
                        'gender': profile.gender,
                        'latitude': profile.latitude,
                        'longitude': profile.longitude,
                        'distance': round(d, 1),
                        'is_online': profile.is_online,
                        'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                        'location_name': profile.location_name or 'Unknown location'
                    })
        
        return JsonResponse({
            'users': users_data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        })

@login_required
def update_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude is not None and longitude is not None:
                # Store location in session
                request.session['user_location'] = {
                    'latitude': latitude,
                    'longitude': longitude
                }
                
                # Update user profile
                profile = request.user.userprofile
                profile.latitude = latitude
                profile.longitude = longitude
                profile.save(update_fields=['latitude', 'longitude'])
                
                return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            pass
    
    return JsonResponse({'status': 'error'}, status=400)
