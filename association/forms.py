from django import forms
from .models import *
from ckeditor_uploader.fields import RichTextUploadingField

NEWS_TYPE = (('協會消息', '協會消息'), ('會員消息', '會員消息'))


class NewsForm(forms.ModelForm):
    title = forms.CharField()
    content = RichTextUploadingField()
    image = forms.ImageField(required=False)
    type = forms.ChoiceField(choices=NEWS_TYPE)

    class Meta:
        model = News
        fields = ('title', 'content', 'image', 'type')


class IntroForm(forms.ModelForm):
    intro = RichTextUploadingField()

    class Meta:
        model = Intro
        fields = ('intro',)
