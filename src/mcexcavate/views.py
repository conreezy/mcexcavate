from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import requests
from requests import Request, Session
import json
from .forms import ContactForm, SodPriceForm
# from houses.models import HouseSale

def home_page(request):
    title = "McExcavate"
    meta_title = "McExcavate Inc. | Ottawa Excavation & Construction"
    meta_description = "McExcavate has been providing Ottawa with residential and commercial excavation services since 2008."
    meta_keywords = ""
    meta_robots = "index, follow"

    template_name = "index.html"
    context = {"title": title, 
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title}
    return render(request, template_name, context)

def excavation_page(request):
    title = "EXCAVATION OTTAWA"
    meta_title = 'Ottawa Excavation Services | McExcavate Inc.'
    meta_description = "McExcavate provides Ottawa Excavation services to commercial, residential and government clients. One of Ottawa's leading excavation companies since 2013."
    meta_keywords = "ottawa excavation, excavation ottawa, excavating ottawa, ottawa excavating, excavation services, ottawa excavation services, excavation, excavating"
    meta_robots = "index, follow"

    template_name = "excavation.html"
    context = {"title": title, 
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title}
    return render(request, template_name, context)

def interlock_page(request):
    title = "INTERLOCK OTTAWA"
    meta_title = 'Ottawa Interlock | McExcavate Inc.'
    meta_description = "McExcavate produces high quality interlock and hardscape projects to commercial, residential and government clients in Ottawa."
    meta_keywords = "ottawa interlock, interlock ottawa, interlock pathways ottawa, ottawa interlock patio, interlock driveway, ottawa interlock repair, "
    meta_robots = "index, follow"

    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,}
    return render(request, "interlock.html", context)

def re_sodding_page(request):
    title = "SOD INSTALLATION OTTAWA"
    meta_title = "Sod Installation Ottawa | McExcavate Inc."
    meta_description = "Mcexcavate provides sod installation in Ottawa. We use high quality screeened top soil and make sure the lawn is perfectly graded."
    meta_keywords = "sod installation ottawa, ottawa sod installation, ottawa sod install, sod install ottawa, re-sodding ottawa, ottawa re-sodding, re-sodding, sod installation,"
    meta_robots = "index, follow"
    price = 0 

    form = SodPriceForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
        name_ = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        yard = form.cleaned_data.get('yard').lower()
        length = int(form.cleaned_data.get('length'))
        width = int(form.cleaned_data.get('width'))
        area = int(form.cleaned_data.get('area'))
        
        if yard == "front" and area < 750:
            price = 1687.50
        elif yard == "back" and area < 750:
            price = 1940.63
        elif yard == "front & back" and area < 750:
            price = 1814.06
        elif yard == "front" and area < 3000:
            price = area * 2.25
        elif yard == "back" and area < 3000:
            price = area * 2.59
        elif yard == "front & back" and area < 3000:
            price = area * 2.42
        elif yard == "front" and area >= 3000:
            price = area * 2
        elif yard == "back" and area >= 3000:
            price = area * 2.3
        elif yard == "front & back" and area >= 3000:
            price = area * 2.15
        else:
            price = 9999999

        price = '${:,.2f}'.format(price)

        # send the confirmation email 
        subject = f"McExcavate | Re-Sodding Price Quote"
        message =  f"Hello {name_}, \
                     \n\nThank you for using our pricing calculator. \
                     \n\nRe-Sodding an area of {area} square feet ({length}' x {width}') in your {yard} yard will cost aproximately {price} (accurate to within 10% - 15%). \
                     \n\nFor more information or to book an an in person estimate contact us today. \
                     \n\nMcExcavate \
                     \nOttawa, ON \
                     \n613-608-7722"
        from_address = settings.EMAIL_HOST_USER
        to_address = email
        send_mail(subject, message, from_address, [to_address], fail_silently=False)

        messages.success(request, f"{ price } to re-sod { area } square feet in your { yard } yard.")

    template_name = "re-sodding.html"
    context = {
               "title": title, 
               "form":form,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "price":price}
    return render(request, template_name, context)

def maintenance_page(request):
    title = "LAWN MOWING OTTAWA"
    meta_title = 'Lawn Mowing Ottawa | McExcavate Inc.'
    meta_description = "McExcavate provides Ottawa lawn mowing services to commercial, residential and government clients. One of Ottawa's leading lawn maintenance companies since 2013."
    meta_keywords = "ottawa lawn mowing, lawn mowing ottawa, lawn maintenance ottawa, ottawa lawn maintenance, grass mowing, ottawa grass mowing, over-seeding, fertilizing, aeration, hedge trimming, top dressing"
    meta_robots = "index, follow"

    template_name = "maintenance.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title}
    return render(request, template_name, context)

def concrete_page(request):
    title = "STAMPED CONCRETE OTTAWA"
    meta_title = 'Stamped Concrete Ottawa | McExcavate Inc.'
    meta_description = "McExcavate provides stamped concrete installation to commercial, residential and government clients. One of Ottawa's leading stamped concrete companies since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"

    template_name = "concrete.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title}
    return render(request, template_name, context)

def asphalt_page(request):
    title = "ASPHALT DRIVEWAY PAVING OTTAWA"
    meta_title = 'Asphalt Driveway Paving Ottawa | McExcavate Inc.'
    meta_description = "McExcavate provides asphalt driveway paving to Ottawa, residential and commercial clients. We have been one of Ottawa's leading asphalt paving companies since 2013."
    meta_keywords = "driveway paving ottawa, ottawa driveway paving, asphalt driveway paving ottawa, ottawa asphalt driveway paving,\
                     ottawa asphalt driveways, asphalt driveways ottawa, ottawa paving, paving ottawa, driveway paving,\
                     asphalt ottawa, ottawa asphalt,"
    meta_robots = "index, follow"

    template_name = "asphalt-paving.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title}
    return render(request, template_name, context)

def asphalt_repairs_page(request):
    title = "ASPHALT REPAIRS OTTAWA"
    meta_title = 'Asphalt Repairs Ottawa | McExcavate Inc.'
    meta_description = "McExcavate does asphalt repairs including ramps, pathces and pot holes. Since 2013 we have done residential, commercial and government contracts"
    meta_keywords = "ottawa asphalt repairs, asphalt repairs ottawa, asphalt repairs"
    meta_robots = "index, follow"

    template_name = "asphalt-repairs.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title}
    return render(request, template_name, context)

def parging_page(request):
    title = "PARGING OTTAWA"
    meta_title = 'Parging Ottawa | McExcavate Inc.'
    meta_description = "McExcavate provides parging services to commercial, residential and government clients. One of Ottawa's leading parging service providers since 2013."
    meta_keywords = "ottawa parging, parging ottawa"
    meta_robots = "index, follow"

    template_name = "parging.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title}
    return render(request, template_name, context)

def careers_page(request):
    title = "OTTAWA CONSTRUCTION JOBS"
    meta_title = 'Ottawa Construction Jobs | Careers With McExcavate'
    meta_description = "McExcavate has been employing people in the construction industry since 2013. We pride outselves on being an excellent employer and having a great work environment."
    meta_keywords = "ottawa construction jobs, construction jobs ottawa, equipment operator job ottawa, landscaping jobs ottawa, construction careers ottawa, construction foreman job ottawa, landscape foreman ottawa"
    meta_robots = "index, follow"

    template_name = "careers.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title}
    return render(request, template_name, context)

def about_page(request):
    title = "ABOUT"
    meta_title = 'About Us | McExcavate Inc.'
    meta_description = "Our work is done to the highest quality standards."
    meta_keywords = "mcexcavate ottawa, mcexcavate, mcexcavate inc"
    meta_robots = "index, follow"

    template_name = "about.html"
    context = {"title": title,}
               # "meta_description":meta_description,
               # "meta_robots":meta_robots,
               # "meta_keywords":meta_keywords,
               # "meta_title":meta_title} 
    return render(request, template_name, context)

def contact_page(request):
    title = "CONTACT US"
    meta_title = 'Contact Us | McExcavate Inc. | Ottawa'
    meta_description = "Contact Us by phone, email or send a message through our website."
    meta_keywords = ""
    meta_robots = "index, follow"

    form = ContactForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
        name = form.cleaned_data.get("name")
        email = form.cleaned_data.get("email")
        address = form.cleaned_data.get("address")
        service = form.cleaned_data.get("service")
        content = form.cleaned_data.get("content")

        # send the confirmation email  
        subject = f'McExcavate Contact Request: {service}'
        message =  f'McExcavate Contact Request: \
                     \n\n name: {name} \
                     \n\n email: {email} \
                     \n\n address: {address} \
                     \n\n service: {service} \
                     \n\n content: {content}'
        from_address = settings.EMAIL_HOST_USER
        to_address = "conormcveigh88@gmail.com"
        send_mail(subject, message, from_address, [to_address], fail_silently=False)

        messages.success(request, f"Thank you for contacting us { name }. We will get back to you quickly with more information about our {service} service.")

        form = ContactForm()

    template_name = "contact.html"
    context = {
        "title": title, 
        "form": form,}
        # "meta_description":meta_description,
        # "meta_robots":meta_robots,
        # "meta_keywords":meta_keywords,
        # "meta_title":meta_title}    
    return render(request, template_name, context)