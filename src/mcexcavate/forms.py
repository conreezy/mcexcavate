from django import forms

Excavation = "Excavation"
ReSodding =  "Re-Sodding"
Interlock =  "Interlock"
Concrete =  "Concrete"
AsphaltPaving =  "Asphalt Paving"
AsphaltRepairs =  "Asphalt Repairs"

SERVICE_CHOICES = (
  (Excavation, 'Excavation'),
  (ReSodding, 'Re-Sodding'),
  (Interlock, 'Interlock'),
  (Concrete, 'Concrete'),
  (AsphaltPaving, 'Asphalt Paving'),
  (AsphaltRepairs, 'Asphalt Repairs'),
  )

class ServicePageContactForm(forms.Form):
    name    = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email   = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    address    = forms.CharField(label='Address', widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    service = forms.ChoiceField(label='Service Required', choices=SERVICE_CHOICES, 
                                                          widget=forms.HiddenInput(attrs={'id':'form_service'}))
    content = forms.CharField(label='Description of Work',widget=forms.Textarea(attrs={'placeholder': "Please give us an idea of what you're looking to do so we can respond in greater detail."}), required=False)

class ContactPageContactForm(forms.Form):
    name    = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email   = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    address    = forms.CharField(label='Address', widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    service = forms.ChoiceField(label='Service Required', choices=SERVICE_CHOICES, 
                                                          widget=forms.Select(attrs={'id':'form_service'}))
    content = forms.CharField(label='Description of Work',widget=forms.Textarea(attrs={'placeholder': "Please give us an idea of what you're looking to do so we can respond in greater detail."}), required=False)

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
    