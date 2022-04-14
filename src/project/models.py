from django.db import models
from django.conf import settings


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