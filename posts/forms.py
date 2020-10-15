from django import forms

from .models import Post, Group, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        help_texts = {
                      'text': 'Текст',
                      'group': 'Группа',
                      'image': 'Картинка',
                      }

    group = forms.ModelChoiceField(queryset=Group.objects.all(),
                                   required=False)
    text = forms.CharField(widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        help_texts = {
                      'text': 'Текст',
                      'group': 'Группа',
                      }

    text = forms.CharField(widget=forms.Textarea)
