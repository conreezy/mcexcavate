from django.db import models
from django.conf import settings
from django.utils import timezone


User = settings.AUTH_USER_MODEL

# class ExcavationEstimate(models.Model):
#     name     = models.CharField(max_length=100, blank=True)
#     email    = models.CharField(max_length=100, blank=True)
#     address  = models.CharField(max_length=100, blank=True)
#     service  = models.CharField(max_length=100, blank=True)
#     location = models.CharField(max_length=100, blank=True)
#     length   = models.CharField(max_length=100, blank=True)
#     width    = models.CharField(max_length=100, blank=True)
#     area     = models.CharField(max_length=100, blank=True)
#     price    = models.CharField(max_length=100, blank=True) 

# class InterlockEstimate(models.Model):
#     name     = models.CharField(max_length=100, blank=True)
#     email    = models.CharField(max_length=100, blank=True)
#     address  = models.CharField(max_length=100, blank=True)
#     service  = models.CharField(max_length=100, blank=True)
#     location = models.CharField(max_length=100, blank=True)
#     length   = models.CharField(max_length=100, blank=True)
#     width    = models.CharField(max_length=100, blank=True)
#     area     = models.CharField(max_length=100, blank=True)
#     price    = models.CharField(max_length=100, blank=True) 

class PavingEstimate(models.Model):
    name     = models.CharField(max_length=100, blank=True)
    email    = models.CharField(max_length=100, blank=True)
    address  = models.CharField(max_length=100, blank=True)
    pave_type  = models.CharField(max_length=100, blank=True)
    length   = models.CharField(max_length=100, blank=True)
    width    = models.CharField(max_length=100, blank=True)
    area     = models.CharField(max_length=100, blank=True)
    price    = models.CharField(max_length=100, blank=True) 
    date     = models.DateTimeField(auto_now_add=True)

# class AsphaltRepairEstimate(models.Model):
#     name     = models.CharField(max_length=100, blank=True)
#     email    = models.CharField(max_length=100, blank=True)
#     address  = models.CharField(max_length=100, blank=True)
#     service  = models.CharField(max_length=100, blank=True)
#     location = models.CharField(max_length=100, blank=True)
#     length   = models.CharField(max_length=100, blank=True)
#     width    = models.CharField(max_length=100, blank=True)
#     area     = models.CharField(max_length=100, blank=True)
#     price    = models.CharField(max_length=100, blank=True) 

# class ConcreteEstimate(models.Model):
#     name     = models.CharField(max_length=100, blank=True)
#     email    = models.CharField(max_length=100, blank=True)
#     address  = models.CharField(max_length=100, blank=True)
#     service  = models.CharField(max_length=100, blank=True)
#     location = models.CharField(max_length=100, blank=True)
#     length   = models.CharField(max_length=100, blank=True)
#     width    = models.CharField(max_length=100, blank=True)
#     area     = models.CharField(max_length=100, blank=True)
#     price    = models.CharField(max_length=100, blank=True) 

class SodEstimate(models.Model):
    name     = models.CharField(max_length=100, blank=True)
    email    = models.CharField(max_length=100, blank=True)
    address  = models.CharField(max_length=100, blank=True)
    yard     = models.CharField(max_length=100, blank=True)
    length   = models.FloatField(max_length=100, blank=True)
    width    = models.FloatField(max_length=100, blank=True)
    area     = models.FloatField(max_length=100, blank=True)
    price    = models.FloatField(max_length=100, blank=True, null=True) 
    date     = models.DateTimeField(auto_now_add=True)


class LeadSubmission(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'

    EMAIL_STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    )

    source_page = models.CharField(max_length=150, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    service = models.CharField(max_length=150, blank=True)
    marketing = models.CharField(max_length=150, blank=True)
    message = models.TextField(blank=True)
    recipient_emails = models.TextField(blank=True)
    email_status = models.CharField(max_length=20, choices=EMAIL_STATUS_CHOICES, default=STATUS_PENDING)
    email_error = models.TextField(blank=True)
    emailed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.service} - {self.created_at:%Y-%m-%d %H:%M}"

    def as_form_data(self):
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'marketing': self.marketing,
            'service': self.service,
            'content': self.message,
        }

    def mark_email_sent(self):
        self.email_status = self.STATUS_SENT
        self.email_error = ''
        self.emailed_at = timezone.now()
        self.save(update_fields=['email_status', 'email_error', 'emailed_at', 'updated_at'])

    def mark_email_failed(self, error):
        self.email_status = self.STATUS_FAILED
        self.email_error = str(error)
        self.save(update_fields=['email_status', 'email_error', 'updated_at'])


class LeadSubmissionImage(models.Model):
    lead = models.ForeignKey(LeadSubmission, related_name='images', on_delete=models.CASCADE)
    file = models.FileField(max_length=500)
    original_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.original_name or self.file.name

    @property
    def absolute_path(self):
        return self.file.path

    
class Project(models.Model):
    user           = models.ForeignKey(User, max_length=10000, blank=True, null=True, on_delete=models.CASCADE)
    #proj_id        =
    # excavation     = models.OneToOneField(max_length=100, blank=True)
    # interlock      = models.OneToOneField(max_length=100, blank=True)
    # asphalt_pave   = models.OneToOneField(max_length=100, blank=True)
    # asphalt_repair = models.OneToOneField(max_length=100, blank=True)
    # concrete       = models.OneToOneField(max_length=100, blank=True)
    # sod 		   = models.OneToOneField(max_length=100, blank=True)
    
    price          = models.FloatField(max_length=100, blank=True)
    hst			   = models.FloatField(max_length=100, blank=True)
    total_price    = models.FloatField(max_length=100, blank=True)
    deposit		   = models.FloatField(max_length=100, blank=True)
    
    payment1       = models.FloatField(max_length=100, blank=True)
    payment2       = models.FloatField(max_length=100, blank=True)
    payment3       = models.FloatField(max_length=100, blank=True)
    payment4       = models.FloatField(max_length=100, blank=True)
    discount	   = models.FloatField(max_length=100, blank=True)
    balance        = models.FloatField(max_length=100, blank=True)


# class Invoice(models.Model):
# 	project = models.ForeignKey(max_length=10000, blank=True, null=True)
# 	type_   =
# 	status  = 
