from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост (необязательно)',
        }
