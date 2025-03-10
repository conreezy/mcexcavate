from django import forms
from .models import Gallery, GalleryImages
from django.forms import ClearableFileInput, ModelChoiceField

class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title

class GalleryForm(forms.ModelForm):
    title   = forms.CharField(widget=forms.TextInput(attrs={'label':'Page Title', 'placeholder': 'Page Title'}))
    slug    = forms.SlugField(widget=forms.TextInput(attrs={'placeholder': 'Slug'}))
    meta_title = forms.CharField(widget=forms.TextInput(attrs={'label':'Meta Title', 'placeholder': 'Meta Title'}))
    description = forms.CharField(max_length=160, 
                                      widget=forms.Textarea(attrs={'placeholder': 'Text that will be displayed on Google search results under the title. 160 characters max.'}))
    meta_keywords = forms.CharField(max_length=200, 
                                   widget=forms.Textarea(attrs={'placeholder': 'Add a few SEO keywords. Seperated by commas. EX: keyword1, keyword2, keyword3'}))

    class Meta:
    	model = Gallery
    	fields = ['title', 'image', 'slug', 'meta_title', 'description', 'meta_keywords']

class GalleryImagesForm(forms.ModelForm):
    class Meta:
        model = GalleryImages
        fields = ['images']
        widgets = {'images': ClearableFileInput(attrs={'multiple':True})}


class GalleryEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GalleryEditForm, self).__init__(*args, **kwargs)
        self.fields['gallery'].queryset = Gallery.objects.all()

    gallery = MyModelChoiceField(label='Gallery', 
                                 queryset=None, 
                                 widget=forms.Select(attrs={'id':'galleries'}))

    class Meta:
        model = GalleryImages
        fields = ['images', 'gallery']
        widgets = {'images': ClearableFileInput(attrs={'multiple':True})}