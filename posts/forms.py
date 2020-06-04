from django import forms
from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text']
        labels = {
            'group': 'Группа',
            'text': 'Ваш текст'
        }

    def clean_text(self):
        data = self.cleaned_data['text']

        if len(data) < 100:
            raise forms.ValidationError ('Слишком короткий текст, мы любим графоманов!')

        return data
