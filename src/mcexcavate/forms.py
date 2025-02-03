from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.utils.safestring import mark_safe
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox, ReCaptchaV2Invisible

Default = "---"
Excavation = "Excavation"
SodInstallation =  "Sod Installation"
Interlock =  "Interlock"
Concrete =  "Concrete"
Parging =  "Parging"
Bollards = "Bollards"

SERVICE_CHOICES = (
  (Default, '---'),
  (Concrete, 'Concrete'),
  (SodInstallation, 'Sod Installation'),
  (Interlock, 'Interlock'),
  (Excavation, 'Excavation'),
  (Parging, 'Parging'),
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

class CustomReCaptchaV2Checkbox(ReCaptchaV2Checkbox):
    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        if 'class' in attrs:
            attrs['class'] = attrs['class'].replace('form-control', '')  # Remove form-control class
        return attrs
    
class ServicePageContactForm(forms.Form):
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
    images = forms.ImageField(label='Images (Max 5)',
                              widget=forms.ClearableFileInput(attrs={
                                'multiple': True,
                                'accept': 'image/*'
                              }),
                              required=False,
                              help_text=mark_safe("Send us some photos to give a better idea about your project. <br> \
                                         Upload up to 5 images (max size: 10MB each).") 
                             )
    marketing = forms.ChoiceField(label='How did you hear about us?', choices=MARKETING_CHOICES)
    captcha = ReCaptchaField(label='', widget=CustomReCaptchaV2Checkbox)

class ContactPageContactForm(forms.Form):
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
    images = forms.ImageField(label='Images (Max 5)',
                              widget=forms.ClearableFileInput(attrs={
                                'multiple': True,
                                'accept': 'image/*'
                              }),
                              required=False,
                              help_text=mark_safe("Send us some photos to give a better idea about your project. <br> \
                                         Upload up to 5 images (max size: 10MB each).") 
                             )
    marketing = forms.ChoiceField(label='How did you hear about us?', choices=MARKETING_CHOICES)
    captcha = ReCaptchaField(label='', widget=CustomReCaptchaV2Checkbox)


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
    