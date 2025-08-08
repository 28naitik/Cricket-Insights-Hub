from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share something about cricket...',
                'class': 'form-control w-full',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'content': '',
            'image': 'Attach an image (optional)',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'Write a comment...',
                'class': 'form-control w-full',
            }),
        }
        labels = {
            'text': '',
        }