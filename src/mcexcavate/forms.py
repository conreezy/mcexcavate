from django import forms
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from django.utils.safestring import mark_safe
from PIL import Image, UnidentifiedImageError
try:
    from django_recaptcha.fields import ReCaptchaField
    from django_recaptcha.widgets import ReCaptchaV3
except ModuleNotFoundError:
    from captcha.fields import ReCaptchaField
    from captcha.widgets import ReCaptchaV3

Default = "---"
Excavation = "Excavation"
StampedConcrete = "Stamped Concrete"
ConcreteSlabs = "Concrete Slabs"
ConcreteSteps = "Concrete Steps"
ConcreteRepairs = "Concrete Repairs"
ConcreteResurfacing = "Concrete Resurfacing"
Bollards = "Bollards"

SERVICE_CHOICES = (
  (Default, '---'),
  (StampedConcrete, 'Stamped Concrete'),
  (ConcreteSlabs, 'Concrete Slabs'),
  (ConcreteSteps, 'Concrete Steps'),
  (ConcreteRepairs, 'Concrete Repairs'),
  (ConcreteResurfacing, 'Concrete Resurfacing'),
  (Excavation, 'Excavation'),
  (Bollards, 'Bollards'),
  )

Default = "---"
GoogleSearch = "Google Search"
Flyer = "Flyer"
Referal =  "Referal"
Other =  "Other"

MARKETING_CHOICES = (
  (Default, '---'),
  (GoogleSearch, 'Google Search'),
  (Flyer, 'Flyer'),
  (Referal, 'Referal'),
  (Other, 'Other'),
  )

class CustomReCaptchaV3(ReCaptchaV3):
    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        if 'class' in attrs:
            attrs['class'] = attrs['class'].replace('form-control', '')
        return attrs


MAX_CONTACT_UPLOAD_IMAGES = 5


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs.setdefault('multiple', True)
        super().__init__(attrs)


class MultipleImageFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        single_file_clean = super().clean
        return [single_file_clean(item, initial) for item in data]


def validate_contact_images(uploaded_images):
    errors = []

    if len(uploaded_images) > MAX_CONTACT_UPLOAD_IMAGES:
        errors.append(
            f"You can upload up to {MAX_CONTACT_UPLOAD_IMAGES} images, but you selected {len(uploaded_images)}."
        )

    for uploaded_image in uploaded_images:
        try:
            uploaded_image.seek(0)
            with Image.open(uploaded_image) as img:
                img.verify()
            uploaded_image.seek(0)
        except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
            uploaded_image.seek(0)
            errors.append(f"{uploaded_image.name}: The file is not a valid image.")

    if errors:
        raise ValidationError(errors)

    return uploaded_images


class BaseContactForm(forms.Form):
    def clean_images(self):
        uploaded_images = self.files.getlist('images')
        if not uploaded_images:
            return []
        return validate_contact_images(uploaded_images)

class ServicePageContactForm(BaseContactForm):
    name    = forms.CharField(label='Name', 
                              widget=forms.TextInput(attrs={}))
    email   = forms.EmailField(label='Email', 
                               widget=forms.TextInput(attrs={}))
    phone   = PhoneNumberField(label= 'Phone', 
                               region="CA", 
                               widget=forms.TextInput(attrs={}))
    address = forms.CharField(label='Address', 
                              widget=forms.TextInput(attrs={}))
    service = forms.ChoiceField(label='Service Required', 
                                choices=SERVICE_CHOICES, 
                                widget=forms.HiddenInput(attrs={
                                    'id':'form_service'}))
    content = forms.CharField(label='Message',
                              widget=forms.Textarea(attrs={
                                'placeholder': "Describe your project here.",
                                'rows':'3'
                              }), 
                              required=False)
    images = MultipleImageFileField(label='Images (Max 5)',
                              widget=MultipleFileInput(attrs={
                                'accept': 'image/*'
                              }),
                              required=False,
                              help_text=mark_safe("Send us some photos to give a better idea about your project. <br> \
                                         Upload up to 5 images (max size: 10MB each).") 
                             )
    marketing = forms.ChoiceField(label='How did you hear about us?', choices=MARKETING_CHOICES)
    captcha = ReCaptchaField(label='', widget=CustomReCaptchaV3())

class ContactPageContactForm(BaseContactForm):
    name    = forms.CharField(label='Name', 
                              widget=forms.TextInput(attrs={}))
    email   = forms.EmailField(label='Email', 
                               widget=forms.TextInput(attrs={}))
    phone   = PhoneNumberField(label= 'Phone', 
                               region="CA", 
                               widget=forms.TextInput(attrs={}))
    address = forms.CharField(label='Address', 
                              widget=forms.TextInput(attrs={}))
    service = forms.ChoiceField(label='Service Required', 
                                choices=SERVICE_CHOICES, 
                                widget=forms.Select(attrs={
                                    'id':'form_service'}))
    content = forms.CharField(label='Message',
                              widget=forms.Textarea(attrs={
                                'placeholder': "Describe your project here.",
                                'rows':'3'
                              }), 
                              required=False)
    images = MultipleImageFileField(label='Images (Max 5)',
                              widget=MultipleFileInput(attrs={
                                'accept': 'image/*'
                              }),
                              required=False,
                              help_text=mark_safe("Send us some photos to give a better idea about your project. <br> \
                                         Upload up to 5 images (max size: 10MB each).") 
                             )
    marketing = forms.ChoiceField(label='How did you hear about us?', choices=MARKETING_CHOICES)
    captcha = ReCaptchaField(label='', widget=CustomReCaptchaV3())


YARD_CHOICES = (
    ('Front', 'Front'),
    ('Back', 'Back'),
    ('Front & Back', 'Front & Back'),
    )

class SodPriceForm(forms.Form):
    name    = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email   = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    address = forms.CharField(label='Address', widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    yard    = forms.ChoiceField(label='Lawn Location', choices=YARD_CHOICES)
    length  = forms.FloatField(label='Length', widget=forms.TextInput(attrs={'placeholder': 'Length', 
                                                                             'oninput': 'changeArea()',
                                                                             'id':'length'}))

    width   = forms.FloatField(label='Width', widget=forms.TextInput(attrs={'placeholder': 'Width', 
                                                                            'oninput': 'changeArea()',
                                                                            'id':'width'}))

    area    = forms.FloatField(label='Total Area', widget=forms.TextInput(attrs={'placeholder': 'Total Area', 
                                                                                 'oninput': 'changeLengthWidth()',
                                                                                 'id':'area'}))

PAVE_CHOICES = (
    ('Remove old asphalt & pave', 'Remove old asphalt & pave'),
    ('Pave only', 'Pave only')
    )

class PavingPriceForm(forms.Form):
    name    = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email   = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    address = forms.CharField(label='Address', widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    pave_type = forms.ChoiceField(label='Pave Type', 
                                  choices=PAVE_CHOICES, 
                                  widget=forms.Select(attrs={'id':'pave_type'}))
    length  = forms.FloatField(label='Length', widget=forms.TextInput(attrs={'placeholder': 'Length', 
                                                                               'oninput': 'changeArea()',
                                                                               'id':'length'}))
    width   = forms.FloatField(label='Width', widget=forms.TextInput(attrs={'placeholder': 'Width', 
                                                                              'oninput': 'changeArea()',
                                                                              'id':'width'}))

    area    = forms.FloatField(label='Total Area', widget=forms.TextInput(attrs={'placeholder': 'Total Area', 
                                                                                   'oninput': 'changeLengthWidth()',
                                                                                   'id':'area'}))
    
