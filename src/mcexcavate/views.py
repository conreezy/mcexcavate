from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse
from django.template.loader import get_template
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import requests
from requests import Request, Session
import json
from project.models import SodEstimate, PavingEstimate
from .forms import ServicePageContactForm, ContactPageContactForm, SodPriceForm, PavingPriceForm
from blog.models import BlogPost

def home_page(request):
    title = "McExcavate"
    meta_title = "McExcavate | Ottawa Concrete Contractor"
    meta_description = "McExcavate is an Ottawa based concrete contractor specializing in stamped concrete, patios, \
                        driveways, steps, concrete repairs and concrete sealing since 2013."
    meta_keywords = "ottawa concrete company, concrete company ottawa, ottawa concrete contractor, \
                     concrete contractor ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    template_name = "index.html"
    context = {"title": title, 
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,}
    return render(request, template_name, context)

def services_page(request):
    title = "OUR SERVICES"
    meta_title = 'Our Services | McExcavate Inc.'
    meta_description = "We are stamped concrete experts, we also do concrete slabs, steps, sidewalks and curbs. \
                        Additionaly we do sod installation, interlock and excavation"
    meta_keywords = "mcexcavate construction services"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/services/"
    og_image = "https://mcexcavate.com/static/image/excavation/large yellow komatsu excavator.jpg"
    og_type = "website"

    template_name = "services.html"
    context = {"title": title, 
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,}
    return render(request, template_name, context)

def excavation_page(request):
    title = "EXCAVATION OTTAWA"
    breadcrumbs_title = "Excavation"
    meta_title = 'Ottawa Excavation Services | McExcavate Inc.'
    meta_description = "McExcavate provides Ottawa Excavation services to commercial, residential and government clients. One of Ottawa's leading excavation companies since 2013."
    meta_keywords = "ottawa excavation, excavation ottawa, excavating ottawa, ottawa excavating, excavation services, ottawa excavation services, excavation, excavating"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/excavation/"
    og_image = "https://mcexcavate.com/static/image/excavation/large yellow komatsu excavator.jpg"
    og_type = "website"

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Excavation")  

    template_name = "excavation.html"
    context = {"title": title, 
               "blogs":blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title" : breadcrumbs_title}
    return render(request, template_name, context)

def interlock_page(request):
    title = "INTERLOCK OTTAWA"
    breadcrumbs_title = "Interlock"
    meta_title = 'Ottawa Interlock | McExcavate'
    meta_description = "McExcavate produces high quality interlock and hardscape projects to commercial, residential and government clients in Ottawa."
    meta_keywords = "ottawa interlock, interlock ottawa, interlock pathways ottawa, ottawa interlock patio, interlock driveway, ottawa interlock repair, "
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/interlock/"
    og_image = "https://mcexcavate.com/static/image/interlock/black with grey border interlock front step and walkway.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Interlock Lead | Interlock Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Interlock")  

    context = {"title": title,
               "blogs":blogs,
               "form":form,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, "interlock.html", context)

def re_sodding_page(request):
    title = "SOD INSTALLATION OTTAWA"
    breadcrumbs_title = "Sod Installation"
    meta_title = "Sod Installation Ottawa | McExcavate"
    meta_description = "McExcavate has been providing sod installation in Ottawa since 2013. We use high quality top soil and make sure the lawn is perfectly graded before laying sod."
    meta_keywords = "sod installation ottawa, ottawa sod installation, ottawa sod install, sod install ottawa, re-sodding ottawa, ottawa re-sodding, re-sodding, sod installation,"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/sod-installation/"
    og_image = "https://mcexcavate.com/static/image/sod/1_sod_gallery.jpg"
    og_type = "website"

    # price = 0 

    # form = SodPriceForm(request.POST or None)
    # if form.is_valid():
    #     print(form.cleaned_data)
    #     name_ = form.cleaned_data.get('name')
    #     email = form.cleaned_data.get('email')
    #     yard = form.cleaned_data.get('yard').lower()
    #     length = int(form.cleaned_data.get('length'))
    #     width = int(form.cleaned_data.get('width'))
    #     area = int(form.cleaned_data.get('area'))
        
    #     if yard == "front" and area < 750:
    #         price = 1687.50
    #     elif yard == "back" and area < 750:
    #         price = 1940.63
    #     elif yard == "front & back" and area < 750:
    #         price = 1814.06
    #     elif yard == "front" and area < 3000:
    #         price = area * 2.25
    #     elif yard == "back" and area < 3000:
    #         price = area * 2.59
    #     elif yard == "front & back" and area < 3000:
    #         price = area * 2.42
    #     elif yard == "front" and area >= 3000:
    #         price = area * 2
    #     elif yard == "back" and area >= 3000:
    #         price = area * 2.3
    #     elif yard == "front & back" and area >= 3000:
    #         price = area * 2.15
    #     else:
    #         price = 9999999

    #     sod_estimate = SodEstimate.objects.create(**form.cleaned_data)
    #     sod_estimate.price = price
    #     sod_estimate.save()

    #     price = '${:,.2f}'.format(price)       

    #     # send the confirmation email 
    #     subject = f"McExcavate | Re-Sodding Price Quote"
    #     message =  f"Hello {name_}, \
    #                  \n\nThank you for using our pricing calculator. \
    #                  \n\nRe-Sodding an area of {area} square feet ({length}' x {width}') in your {yard} yard will cost aproximately {price} (accurate to within 10% - 15%). \
    #                  \n\nFor more information or to book an an in person estimate contact us today. \
    #                  \n\nMcExcavate \
    #                  \nOttawa, ON \
    #                  \n613-608-7722"
    #     from_address = settings.EMAIL_HOST_USER
    #     to_address = email
    #     send_mail(subject, message, from_address, [to_address], fail_silently=False)
    #     send_mail(subject, message, from_address, ['mcexcavate.ottawa@gmail.com'], fail_silently=False)

    #     messages.success(request, f"{ price } to re-sod { area } square feet in your { yard } yard.")

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Sod Lead | Re-Sodding Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Re-Sodding")

    template_name = "re-sodding.html"
    context = {"title":title, 
               "blogs":blogs,
               "form":form,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def maintenance_page(request):
    title = "LAWN MOWING OTTAWA"
    meta_title = 'Lawn Mowing Ottawa | McExcavate'
    meta_description = "McExcavate provides lawn mowing services in Ottawa to residential and commercial clients. Weekly lawn cutting and season long lawn maintenance and lawn care."
    meta_keywords = "ottawa lawn mowing, lawn mowing ottawa, lawn maintenance ottawa, ottawa lawn maintenance, grass mowing, ottawa grass mowing, over-seeding, fertilizing, aeration, hedge trimming, top dressing"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/lawn-mowing/"

    template_name = "maintenance.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical}
    return render(request, template_name, context)

def concrete_page(request):
    title = "STAMPED CONCRETE OTTAWA"
    breadcrumbs_title = "Stamped Concrete"
    meta_title = 'Stamped Concrete Ottawa | McExcavate'
    meta_description = "McExcavate specializes in stamped concrete in Ottawa. We have been \
                        building stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, stamped concrete, stamped concrete ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Concrete Lead | Concrete Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()
        return HttpResponseRedirect('success/')

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "concrete2.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def concrete_success_page(request):
    title = "Thank you! \
             You are one step closer to becoming another happy customer!"
    meta_title = 'Thank you for contacting us! -McExcavate'
    meta_description = "Thank you for contacting us about your stamped concrete project! \
                        We will be in touch soon to answer your questions or set up an estimate."
    meta_keywords = ""
    meta_robots = "noindex, nofollow" 
    canonical = "https://mcexcavate.com/concrete/success/"
      
    template_name = "concrete-success.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical}
    return render(request, template_name, context)

def stamped_driveway_page(request):
    title = "STAMPED CONCRETE DRIVEWAYS OTTAWA"
    breadcrumbs_title = "Stamped Concrete Driveways"
    meta_title = 'Stamped Concrete Driveways Ottawa | McExcavate'
    meta_description = "We've been building stamped concrete driveways in Ottawa for over 10 years. \
                        McExcavate has the expertise to ensure your prjoect is done correctly."
    meta_keywords = "stamped concrete driveway, concrete driveway ottawa, \
                     stamped concrete driveway ottawa, ottawa stamped concrete driveway"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/stamped-driveway/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Stamped Driveway Lead | Stamped Driveway Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "stamped-driveways.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def stamped_patio_page(request):
    title = "STAMPED CONCRETE PATIOS OTTAWA"
    breadcrumbs_title = "Stamped Concrete Patios"
    meta_title = 'Stamped Concrete Patios Ottawa | McExcavate'
    meta_description = "We have been building stamped concrete patios in Ottawa for over 10 years. \
                        Build a beautiful stamped concrete patio to enjoy your yard."
    meta_keywords = "stamped concrete patio, concrete patio ottawa, \
                     stamped concrete patio ottawa, ottawa stamped concrete patio"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/stamped-patio/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Stamped Patio Lead | Stamped Patio Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "stamped-patios.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context) 

def stamped_walkway_page(request):
    title = "STAMPED CONCRETE WALKWAYS OTTAWA"
    breadcrumbs_title = "Stamped Concrete Walkways"
    meta_title = 'Stamped Concrete Walkways Ottawa'
    meta_description = "We have been building stamped concrete walkways in Ottawa for over 10 years. \
                        McExcavate expertise to ensure your prjoect is done correctly."
    meta_keywords = "stamped concrete walkway, concrete walkway ottawa, \
                     stamped concrete walkway ottawa, ottawa stamped concrete walkway"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/stamped-walkway/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Stamped Walkways Lead | Stamped Walkways Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "stamped-walkways.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def concrete_repairs_page(request):
    title = "CONCRETE REPAIRS OTTAWA"
    breadcrumbs_title = "Concrete Repairs"
    meta_title = 'Concrete Repairs Ottawa'
    meta_description = "McExcavate specializes in stamped concrete in Ottawa. We have been building stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/repair/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Concrete Lead | Concrete Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "concrete-repairs.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def concrete_resurfacing_page(request):
    title = "CONCRETE RESURFACING OTTAWA"
    breadcrumbs_title = "Concrete Resurfacing"
    meta_title = 'Concrete Resurfacing Ottawa'
    meta_description = "McExcavate specializes in stamped concrete in Ottawa. We have been building stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/resurfacing/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Concrete Lead | Concrete Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "concrete-resurfacing.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def concrete_sealing_page(request):
    title = "CONCRETE SEALING OTTAWA"
    breadcrumbs_title = "Concrete Sealing"
    meta_title = 'Concrete Sealing Ottawa'
    meta_description = "McExcavate specializes in stamped concrete in Ottawa. We have been building stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/sealing/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/sealing-stamped-concrete.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Concrete Lead | Concrete Sealing Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "concrete-sealing.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def concrete_slabs_page(request):
    title = "CONCRETE SLABS OTTAWA"
    breadcrumbs_title = "Concrete Slabs"
    meta_title = 'Concrete Slabs Ottawa'
    meta_description = "We build concrete slabs from excavation to forming and pouring. \
                        Commercial and residential. Basement and garage floors, shed pads, hot tub pads..."
    meta_keywords = "conrete slabs, concrete slabs ottawa, ottawa concrete slabs"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/slabs/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/smoothfinish.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Concrete Lead | Concrete Slabs Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete") 
      
    template_name = "concrete-slabs.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def concrete_steps_page(request):
    title = "CONCRETE STEPS OTTAWA"
    breadcrumbs_title = "Concrete Steps"
    meta_title = 'Concrete Steps Ottawa'
    meta_description = "McExcavate specializes in stamped concrete in Ottawa. We have been building stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/steps/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Concrete Lead | Concrete Steps Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete") 
      
    template_name = "concrete-steps.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def asphalt_page(request):
    title = "ASPHALT DRIVEWAY PAVING OTTAWA"
    meta_title = 'Asphalt Driveway Paving Ottawa'
    meta_description = "McExcavate provides asphalt driveway paving in Ottawa to residential and commercial clients. We have been one of Ottawa's leading asphalt paving companies since 2013."
    meta_keywords = "driveway paving ottawa, ottawa driveway paving, asphalt driveway paving ottawa, ottawa asphalt driveway paving,\
                     ottawa asphalt driveways, asphalt driveways ottawa, ottawa paving, paving ottawa, driveway paving,\
                     asphalt ottawa, ottawa asphalt,"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/asphalt-paving/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Asphalt Lead | Asphalt Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # price = 0

    # form = PavingPriceForm(request.POST or None)
    # if form.is_valid():
    #     print(form.cleaned_data)
    #     name_ = form.cleaned_data.get('name')
    #     email = form.cleaned_data.get('email')
    #     pave_type = form.cleaned_data.get('pave_type').lower()
    #     length = int(form.cleaned_data.get('length'))
    #     width = int(form.cleaned_data.get('width'))
    #     area = int(form.cleaned_data.get('area'))

    #     if pave_type == "remove old asphalt & pave":
    #       print("peel and pave")
    #       if area < 333:
    #         price = 1998
    #       elif area >= 333:
    #         price = area * 6 
    #     elif pave_type == "pave only":
    #       print("pave")
    #       if area < 333:
    #         price = 1998
    #       elif area >= 333:
    #         price = area * 4.75 

    #     asphalt_estimate = PavingEstimate.objects.create(**form.cleaned_data)
    #     asphalt_estimate.price = price
    #     asphalt_estimate.save()

    #     price = '${:,.2f}'.format(price)       

    #     # send the confirmation email 
    #     subject = f"McExcavate | Asphalt Paving Price Quote"
    #     message =  f"Hello {name_}, \
    #                  \n\nThank you for using our pricing calculator. \
    #                  \n\n{price} to pave your {area} square foot driveway. (accurate to within 10% - 15%) \
    #                  \n\nFor more information or to book an an in person estimate contact us today. \
    #                  \n\nMcExcavate \
    #                  \nOttawa, ON \
    #                  \n613-608-7722"
    #     from_address = settings.EMAIL_HOST_USER
    #     to_address = email
    #     send_mail(subject, message, from_address, [to_address], fail_silently=False)
    #     send_mail(subject, message, from_address, ['mcexcavate.ottawa@gmail.com'], fail_silently=False)

    #     messages.success(request, f"It would cost aproximately { price } to pave your { area } square foot driveway.")
    
    # Blog Posts section
    blogs = BlogPost.objects.filter(service="AsphaltPaving")  

    template_name = "asphalt-paving.html"
    context = {"title": title,
               "form":form,
               "blogs":blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               #"price":price
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,}
    return render(request, template_name, context)

def asphalt_repairs_page(request):
    title = "ASPHALT REPAIRS OTTAWA"
    meta_title = 'Asphalt Repairs Ottawa'
    meta_description = "McExcavate does asphalt repairs including ramps, pathces and pot holes. Since 2013 we have done residential, commercial and government contracts"
    meta_keywords = "ottawa asphalt repairs, asphalt repairs ottawa, asphalt repairs"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/asphalt-repairs/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Concrete Lead | Concrete Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="AsphaltRepairs")

    template_name = "asphalt-repairs.html"
    context = {"title": title,
               "blogs":blogs,
               "form":form,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,}
    return render(request, template_name, context)

def parging_page(request):
    title = "PARGING OTTAWA"
    breadcrumbs_title = "Parging"
    meta_title = 'Parging Ottawa | McExcavate'
    meta_description = "McExcavate provides parging services to commercial, residential and government clients. One of Ottawa's leading parging service providers since 2013."
    meta_keywords = "ottawa parging, parging ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/parging/"
    og_image = "https://mcexcavate.com/static/image/parging/white_parging.jpg"
    og_type = "website"

    form = ServicePageContactForm(request.POST or None)
    if form.is_valid():
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        address = form.cleaned_data.get('address')
        service = form.cleaned_data.get('service')
        content = form.cleaned_data.get('content')
        marketing = form.cleaned_data.get('marketing')

        # send the contact form to mcexcavate email 
        subject = f"Concrete Lead | Concrete Page"
        message =  f"Name: {name_} \
                     \n\nEmail: {email} \
                     \n\nPhone: {phone} \
                     \n\nAddress: {address} \
                     \n\nService: {service} \
                     \n\nMarketing: {marketing}\
                     \n\nMessage: {content}"
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)
        messages.success(request, f"Thanks for contacting us. We will get back to you soon.")

        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="AsphaltRepairs")

    template_name = "parging.html"
    context = {"title": title,
               "breadcrumbs_title": breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "form" : form,}
    return render(request, template_name, context)

def careers_page(request):
    title = "OTTAWA CONSTRUCTION JOBS"
    breadcrumbs_title = "Careers"
    meta_title = 'Ottawa Construction Jobs | Careers With McExcavate'
    meta_description = "McExcavate has been employing people in the construction industry since 2013. We pride ourselves on providing a professional, rewarding and fun environment."
    meta_keywords = "ottawa construction jobs, construction jobs ottawa, equipment operator job ottawa, landscaping jobs ottawa, construction careers ottawa, construction foreman job ottawa, landscape foreman ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/careers/"
    og_image = "https://mcexcavate.com/static/image/careers/concrete-finisher.jpg"
    og_type = "website"

    template_name = "careers.html"
    context = {"title": title,
               "breadcrumbs_title": breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,}
    return render(request, template_name, context)

def about_page(request):
    title = "ABOUT MCEXCAVATE"
    breadcrumbs_title = "About Us"
    meta_title = 'About Us | McExcavate Inc.'
    meta_description = "McExcavate is an Ottawa based commercial and residential concrete contractor \
                        founded in 2013. We specialeze in decorative coloured and stamped concrete."
    meta_keywords = "mcexcavate ottawa, mcexcavate, mcexcavate inc"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/about/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    template_name = "about.html"
    context = {"title": title,
               "breadcrumbs_title": breadcrumbs_title,
               "canonical":canonical,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               'og_image' : og_image,
               'og_type' : og_type,} 
    return render(request, template_name, context)

def contact_page(request):
    title = "CONTACT US"
    breadcrumbs_title = "Contact Us"
    meta_title = 'Contact Us | McExcavate'
    meta_description = "Contact Us - Phone: 613-608-7722, Email: info@mcexcavate.com or send a message \
                        through one of our forms. Visit our website for more information..."
    meta_keywords = ""
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/contact/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    form = ContactPageContactForm(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data.get("name")
        email = form.cleaned_data.get("email")
        phone = form.cleaned_data.get("phone")
        address = form.cleaned_data.get("address")
        service = form.cleaned_data.get("service")
        marketing = form.cleaned_data.get("marketing")
        content = form.cleaned_data.get("content")

        # send the confirmation email  
        subject = f'{service} Lead | Contact Page'
        message =  f'Name: {name} \
                     \n\n Email: {email} \
                     \n\n Phone: {phone} \
                     \n\n Address: {address} \
                     \n\n Service: {service} \
                     \n\n Marketing: {marketing} \
                     \n\n content: {content}'
        from_address = settings.EMAIL_HOST_USER
        to_address = "mcexcavate.ottawa@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)

        messages.success(request, f"Thank you for contacting us { name }. We will get back to you quickly about your {service} project.")

        form = ContactPageContactForm()

    template_name = "contact.html"
    context = {
               "title": title, 
               "form": form,
               "breadcrumbs_title": breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,}    
    return render(request, template_name, context)

    # def dashboard_view(request):
    # query = request.GET.get('q')
    # qs = SodEstimate.objects.all()
    # if query is not None:
    #     lookups = Q(name__icontations=query)
    #     qs = SodEstimate.objects.filter(lookups)
    # context = {
    #     "sod_estimates":qs
    # }
    # template_name = "dashboard.html"
    # return render(request, template_name, context)

    #fetched_invoice = btcpay_client.get_invoice('3yX6wNsTsa3UjDLYJNw13E')

class DashboardView(TemplateView):
    template_name = "dashboard.html"
    
    def get_sod_estimates_name(self, *args,**kwargs):
        return SodEstimate.objects.filter(name__icontations=query)

    def get_sod_estimates_address(self, query):
        return SodEstimate.objects.filter(name__icontations=query)
    
    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        title = "DASHBOARD"
        meta_title = 'Dashboard | McExcavate Inc.'
        meta_description = "Manage everything here."
        meta_keywords = "dashboard"
        meta_robots = "noindex, nofollow"

        sod_estimates = SodEstimate.objects.all()

        context = {"title": title,
                  "meta_description":meta_description,
                  "meta_robots":meta_robots,
                  "meta_keywords":meta_keywords,
                  "meta_title":meta_title,
                  "sod_estimates":sod_estimates,
                  } 

        return context