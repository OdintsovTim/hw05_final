from django import forms
from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': 'Группа',
            'text': 'Ваш текст',
            'image': 'Ваше изображение'
        }
        help_texts = {
            'group': 'Можно не выбирать группу',
            'text': 'Минимум 10 символов',
            'image': 'Загружать изображение необзательно'
        }

    def clean_text(self):
        data = self.cleaned_data['text']

        if len(data) < 10:
            raise forms.ValidationError('Слишком короткий текст, мы любим графоманов!')

        return data


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
