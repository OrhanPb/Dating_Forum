from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, BlogPost
from datetime import date

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='You must be at least 18 years old to register.'
    )
    gender = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        initial='Other'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'birth_date', 'gender', 'password1', 'password2']

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise forms.ValidationError('You must be at least 18 years old to register.')
        return birth_date

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'gender', 'height', 'career', 'income', 'contact_info',
            'bio', 'interests', 'profile_picture', 'location_name',
            'preferred_gender', 'preferred_age_min', 'preferred_age_max',
            'preferred_distance'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
            'gender': forms.Select(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]),
        }

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }
