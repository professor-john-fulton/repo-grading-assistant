from django import forms
from .models import Comment

# Form for submitting comments on blog posts
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'content']
        widgets = {
            'name': forms.TextInput({'readonly': 'readonly'}),
            'content': forms.Textarea(),
        }