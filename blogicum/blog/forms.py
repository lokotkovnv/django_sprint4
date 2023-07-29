from django import forms
from django.utils import timezone
from django.forms.widgets import DateTimeInput
from django.contrib.auth import get_user_model

from blog.models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'location', 'pub_date', 'image')
        widgets = {
            'pub_date': DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
        }

    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        self.instance.is_published = pub_date and pub_date < timezone.now()
        return pub_date


User = get_user_model()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
