from django import forms
from .models import Gallery, GalleryImages
from django.forms import ClearableFileInput

class GalleryForm(forms.ModelForm):
    title   = forms.CharField(widget=forms.TextInput(attrs={'label':'Address', 'placeholder': 'Address'}))
    slug    = forms.SlugField(widget=forms.TextInput(attrs={'placeholder': 'Slug'}))
    meta_title = forms.CharField(widget=forms.TextInput(attrs={'label':'Meta Title', 'placeholder': 'Meta Title'}))
    description = forms.CharField(max_length=160, 
                                      widget=forms.Textarea(attrs={'placeholder': 'Text that will be displayed on Google search results under the title. 160 characters max.'}))
    meta_keywords = forms.CharField(max_length=200, 
                                   widget=forms.Textarea(attrs={'placeholder': 'Add a few SEO keywords specific to this stone type. Seperated by commas. EX: keyword1, keyword2, keyword3'}))

    class Meta:
    	model = Gallery
    	fields = ['title', 'image', 'slug', 'meta_title', 'description', 'meta_keywords']

class GalleryImagesForm(forms.ModelForm):
    class Meta:
        model = GalleryImages
        fields = ['images']
        widgets = {'images': ClearableFileInput(attrs={'multiple':True})}