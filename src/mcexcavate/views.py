from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse
from django.template.loader import get_template
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMessage, BadHeaderError
import logging
import requests
from requests import Request, Session
import json
from project.models import SodEstimate, PavingEstimate
from .forms import ServicePageContactForm, ContactPageContactForm, SodPriceForm, PavingPriceForm
from blog.models import BlogPost
import os
from PIL import Image, UnidentifiedImageError
from .settings import MEDIA_ROOT
import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from smtplib import SMTPException
from typing import Optional

MAX_UPLOAD_IMAGES = 5  # Limit to 5 images
logger = logging.getLogger(__name__)
LEAD_EMAIL_RECIPIENTS = [
    'info@crusaderconcrete.ca',
    'estimating@crusaderconcrete.ca',
]

def validate_uploaded_image(image):
    try:
        image.seek(0)
        with Image.open(image) as img:
            img.verify()
        image.seek(0)
        return None
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        image.seek(0)
        return f"{image.name}: The file is not a valid image."


def handle_uploaded_files(images):
    if len(images) > MAX_UPLOAD_IMAGES:
        return None, [
            f"You can upload up to {MAX_UPLOAD_IMAGES} images, but you selected {len(images)}."
        ]

    upload_errors = []
    for image in images:
        validation_error = validate_uploaded_image(image)
        if validation_error:
            upload_errors.append(validation_error)

    if upload_errors:
        return None, upload_errors

    upload_dir = os.path.join(MEDIA_ROOT, 'form_uploads')
    os.makedirs(upload_dir, exist_ok=True)

    file_paths = []
    for image in images:
        file_path = os.path.join(upload_dir, image.name)
        try:
            image.seek(0)
            with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            file_paths.append(file_path)
        except OSError as exc:
            for saved_path in file_paths:
                try:
                    os.remove(saved_path)
                except OSError:
                    pass
            return None, [f"{image.name}: The file could not be uploaded. Please try again."]

    return file_paths, []

def _reject_header_injection(value: str, field_name: str = "value") -> str:
    """
    Prevent CRLF/newline header injection.
    Any header value containing \r or \n is unsafe.
    """
    if value and ("\r" in value or "\n" in value):
        raise ValueError(f"Invalid {field_name}: header injection attempt.")
    return value

def _clean_reply_to_email(raw_email: str) -> Optional[str]:
    """
    Returns a validated email or None if invalid/blank.
    Also rejects newline characters (header injection).
    """
    if not raw_email:
        return None

    email = raw_email.strip()
    _reject_header_injection(email, "email")

    try:
        validate_email(email)
        return email
    except ValidationError:
        return None

def send_email_with_attachments(form_data, file_paths, breadcrumbs_title):
    # Build body (body isn't a header, so newline checks aren't required here)
    email_body = f"""
Name: {form_data.get('name', '')}
Email: {form_data.get('email', '')}
Phone: {form_data.get('phone', '')}
Address: {form_data.get('address', '')}
Marketing: {form_data.get('marketing', '')}
Service: {form_data.get('service', '')}
Message: {form_data.get('content', '')}
"""

    # Protect header fields you control/compose
    service = _reject_header_injection(str(form_data.get("service", "")).strip(), "service")
    breadcrumbs_title = _reject_header_injection(str(breadcrumbs_title).strip(), "breadcrumbs_title")

    reply_to_email = _clean_reply_to_email(form_data.get("email", ""))

    email = EmailMessage(
        subject=f"{service} Lead | {breadcrumbs_title}",
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=LEAD_EMAIL_RECIPIENTS,
        reply_to=[reply_to_email] if reply_to_email else None,
    )

    # Your existing attachment logic
    if file_paths:
        for file_path in file_paths:
            try:
                with open(file_path, 'rb') as attachment:
                    email.attach(
                        os.path.basename(file_path),
                        attachment.read(),
                        'application/octet-stream'
                    )
            except Exception as e:
                print(f"Error attaching file {file_path}: {e}")

    try:
        email.send(fail_silently=False)
    except BadHeaderError:
        # Django detected a bad header (often CRLF injection). Log + handle appropriately.
        raise


def _build_form(form_class, request):
    if request.method == 'POST':
        return form_class(request.POST, request.FILES)
    return form_class()


def _process_contact_form_submission(request, form, breadcrumbs_title, redirect_url):
    if request.method != 'POST':
        return None

    if not form.is_valid():
        messages.error(request, "There was an error in your form submission. Please check the fields and try again.")
        return None

    form_data = form.cleaned_data
    images = request.FILES.getlist('images')
    file_paths, upload_errors = handle_uploaded_files(images) if images else ([], [])

    if upload_errors:
        for upload_error in upload_errors:
            form.add_error('images', upload_error)
        messages.error(request, "Please correct the image upload errors below and try again.")
        return None

    try:
        send_email_with_attachments(form_data, file_paths, breadcrumbs_title)
    except (SMTPException, OSError):
        logger.exception("Lead email delivery failed for %s form.", breadcrumbs_title)
        messages.error(
            request,
            "There was a problem sending your message. Please call us directly or try again later.",
        )
        return None

    messages.success(
        request,
        f"Thank you for contacting us {form_data['name']}. Your information has been submitted.<br><br>"
        f"We will get back to you shortly about your {form_data['service']} project.",
    )
    return HttpResponseRedirect(redirect_url)


def _send_plain_lead_email(form_data, subject):
    message = (
        f"Name: {form_data.get('name')} "
        f"\n\nEmail: {form_data.get('email')} "
        f"\n\nPhone: {form_data.get('phone')} "
        f"\n\nAddress: {form_data.get('address')} "
        f"\n\nService: {form_data.get('service')} "
        f"\n\nMarketing: {form_data.get('marketing')}"
        f"\n\nMessage: {form_data.get('content')}"
    )
    send_mail(subject, message, settings.EMAIL_HOST_USER, LEAD_EMAIL_RECIPIENTS, fail_silently=False)


def _process_plain_lead_form_submission(request, form, subject):
    if not form.is_valid():
        return form

    try:
        _send_plain_lead_email(form.cleaned_data, subject)
    except (SMTPException, OSError):
        logger.exception("Lead email delivery failed for %s.", subject)
        return form

    messages.success(request, "Thanks for contacting us. We will get back to you soon.")
    return ServicePageContactForm()


def home_page(request):
    title = "Crusader Concrete"
    meta_title = "Crusader Concrete | Ottawa Concrete Contractor"
    meta_description =  "Discover Ottawa's top stamped concrete solutions for patios, driveways, and walkways. Enhance your home with durable, stylish designs."
    meta_keywords = "ottawa concrete company, concrete company ottawa, ottawa concrete contractor, concrete contractor ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    template_name = "index.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               'date': date,}
    return render(request, template_name, context)


def services_page(request):
    title = "Our Services"
    meta_title = 'Our Services | Crusader Concrete'
    meta_description = "We are stamped concrete experts, we also do plain concrete, steps, sidewalks and curbs. Additionaly we do sod installation, interlock and excavation"
    meta_keywords = "Crusader Concrete services"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/services/"
    og_image = "https://mcexcavate.com/static/image/excavation/large yellow komatsu excavator.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Services"
    crumb_1 = "Services"

    template_name = "services.html"
    context = {"title": title,
               "crumb_1":crumb_1,
               "breadcrumbs_title":breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "date": date,}
    return render(request, template_name, context)


def concrete_services_page(request):
    title = "Concrete Services"
    meta_title = 'Concrete Services | Crusader Concrete'
    meta_description = "We offer a variety of concrete services such as stamped concrete, broom finished concrete, stairs, repairs and resurfacing"
    meta_keywords = "Concrete services"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete-services/"
    og_image = "https://mcexcavate.com/static/image/excavation/large yellow komatsu excavator.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Concrete Services"
    crumb_1 = "Services"
    crumb_2 = "Concrete"
    crumb_1_link = "/services"

    template_name = "concrete-services.html"
    context = {"title": title,
               "crumb_1_link":crumb_1_link,
               "crumb_1":crumb_1,
               "crumb_2":crumb_2,
               "breadcrumbs_title":breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "date": date,}
    return render(request, template_name, context)


def stamped_concrete_page(request):
    title = "STAMPED CONCRETE OTTAWA"
    breadcrumbs_title = "Stamped Concrete"
    meta_title = 'Stamped Concrete Ottawa | Crusader Concrete'
    meta_description = "Crusader Concrete specializes in stamped concrete in Ottawa. We have been building stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, stamped concrete, stamped concrete ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Stamped Concrete"
    crumb_1 = "Services"
    crumb_2 = "Concrete"
    crumb_3 = "Stamped Concrete"
    crumb_1_link = "/services"
    crumb_2_link = "/concrete-services"

    form = _build_form(ServicePageContactForm, request)
    response = _process_contact_form_submission(request, form, breadcrumbs_title, "/concrete/#contactform")
    if response:
        return response

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")

    template_name = "stamped_concrete.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "crumb_1_link":crumb_1_link,
               "crumb_2_link":crumb_2_link,
               "crumb_1":crumb_1,
               "crumb_2":crumb_2,
               "crumb_3":crumb_3,
               "breadcrumbs_title":breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,
               "date": date,}
    return render(request, template_name, context)


def concrete_slabs_page(request):
    title = "CONCRETE SLABS"
    meta_title = 'Concrete Slabs | Crusader Concrete'
    meta_description = "We build concrete slabs from excavation to forming and pouring. \
                        Commercial and residential. Basement and garage floors, shed pads, hot tub pads..."
    meta_keywords = "concrete slabs ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete-slabs/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/smoothfinish.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Concrete Slabs"
    crumb_1 = "Services"
    crumb_2 = "Concrete"
    crumb_3 = "Concrete Slabs"
    crumb_1_link = "/services"
    crumb_2_link = "/concrete-services"

    form = _build_form(ServicePageContactForm, request)
    response = _process_contact_form_submission(request, form, breadcrumbs_title, "/concrete-slabs/#contactform")
    if response:
        return response

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete") 
      
    template_name = "concrete-slabs.html"
    context = {"title": title,
               "crumb_1_link":crumb_1_link,
               "crumb_2_link":crumb_2_link,
               "crumb_1":crumb_1,
               "crumb_2":crumb_2,
               "crumb_3":crumb_3,
               "breadcrumbs_title":breadcrumbs_title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,
               "date": date,}
    return render(request, template_name, context)

def concrete_steps_page(request):
    title = "CONCRETE STEPS"
    breadcrumbs_title = "Concrete Steps"
    meta_title = 'Concrete Steps Ottawa | Crusader Concrete'
    meta_description = "Crusader specializes in stamped concrete in Ottawa. We have been building \
                        stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete-steps/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Concrete Steps"
    crumb_1 = "Services"
    crumb_2 = "Concrete"
    crumb_3 = "Concrete Steps"
    crumb_1_link = "/services"
    crumb_2_link = "/concrete-services"

    form = _build_form(ServicePageContactForm, request)
    response = _process_contact_form_submission(request, form, breadcrumbs_title, "/concrete-steps/#contactform")
    if response:
        return response

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete") 
      
    template_name = "concrete-steps.html"
    context = {"title": title,
               "crumb_1_link":crumb_1_link,
               "crumb_2_link":crumb_2_link,
               "crumb_1":crumb_1,
               "crumb_2":crumb_2,
               "crumb_3":crumb_3,
               "breadcrumbs_title":breadcrumbs_title,
               "form": form,
               "blogs": blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,
               "date": date,}
    return render(request, template_name, context)

def concrete_repairs_page(request):
    title = "CONCRETE REPAIR OTTAWA"
    breadcrumbs_title = "Concrete Repair"
    meta_title = 'Concrete Repair Ottawa | Crusader Concrete'
    meta_description = "Crusader Concrete specializes in stamped concrete in Ottawa. We have been building \
                        stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete-repair/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Concrete Repair"
    crumb_1 = "Services"
    crumb_2 = "Concrete"
    crumb_3 = "Concrete Repair"
    crumb_1_link = "/services"
    crumb_2_link = "/concrete-services"

    form = _build_form(ServicePageContactForm, request)
    response = _process_contact_form_submission(request, form, breadcrumbs_title, "/concrete-repair/#contactform")
    if response:
        return response

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "concrete-repairs.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "crumb_1_link":crumb_1_link,
               "crumb_2_link":crumb_2_link,
               "crumb_1":crumb_1,
               "crumb_2":crumb_2,
               "crumb_3":crumb_3,
               "breadcrumbs_title":breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,
               "date": date,}
    return render(request, template_name, context)

def concrete_resurfacing_page(request):
    title = "CONCRETE RESURFACING OTTAWA"
    breadcrumbs_title = "Concrete Resurfacing"
    meta_title = 'Concrete Resurfacing Ottawa'
    meta_description = "Crusader Concrete specializes in stamped concrete in Ottawa. We have been building \
                        stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete-resurfacing/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Concrete Resurfacing"
    crumb_1 = "Services"
    crumb_2 = "Concrete"
    crumb_3 = "Concrete Resurfacing"
    crumb_1_link = "/services"
    crumb_2_link = "/concrete-services"

    form = _build_form(ServicePageContactForm, request)
    response = _process_contact_form_submission(request, form, breadcrumbs_title, "/concrete-resurfacing/#contactform")
    if response:
        return response

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "concrete-resurfacing.html"
    context = {"title": title,
               "form": form,
               "blogs": blogs,
               "crumb_1_link":crumb_1_link,
               "crumb_2_link":crumb_2_link,
               "crumb_1":crumb_1,
               "crumb_2":crumb_2,
               "crumb_3":crumb_3,
               "breadcrumbs_title":breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title": breadcrumbs_title,
               "date": date,}
    return render(request, template_name, context)

def excavation_page(request):
    title = "Excavation"
    breadcrumbs_title = "Excavation"
    meta_title = 'Ottawa Excavation Services | Crusader Concrete'
    meta_description = "Crusader Concrete provides Ottawa Excavation services to commercial, residential \
                        and government clients. One of Ottawa's leading excavation companies since 2013."
    meta_keywords = "ottawa excavation, excavation ottawa, excavating ottawa, ottawa excavating, \
                    excavation services, ottawa excavation services, excavation, excavating"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/excavation/"
    og_image = "https://mcexcavate.com/static/image/excavation/large yellow komatsu excavator.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Excavation"
    crumb_1 = "Services"
    crumb_2 = "Excavation"
    crumb_1_link = "/services"

    form = _build_form(ServicePageContactForm, request)
    response = _process_contact_form_submission(request, form, breadcrumbs_title, "/excavation/#contactform")
    if response:
        return response

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Excavation")  

    template_name = "excavation.html"
    context = {"title": title, 
               "blogs":blogs,
               "crumb_1_link":crumb_1_link,
               "crumb_1":crumb_1,
               "crumb_2":crumb_2,
               "breadcrumbs_title":breadcrumbs_title, 
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "breadcrumbs_title" : breadcrumbs_title,
               "date": date,
               "form":form,}
    return render(request, template_name, context)

def bollard_page(request):
    title = "Ottawa Bollards"
    breadcrumbs_title = "Bollards"
    meta_title = 'Ottawa Bollards | Crusader Concrete'
    meta_description = "Crusader Concrete installs bollards for commercial, residential and government clients. \
                        One of Ottawa's leading installers of bollards since 2013."
    meta_keywords = "ottawa bollards, bollards ottawa, security bollards ottawa, ottawa security bollards"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/bollards/"
    og_image = "https://mcexcavate.com/static/image/bollards/man_bollard11.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Bollards"
    crumb_1 = "Services"
    crumb_2 = "Bollards"
    crumb_1_link = "/services"

    form = _build_form(ServicePageContactForm, request)
    response = _process_contact_form_submission(request, form, breadcrumbs_title, "/bollards/#contactform")
    if response:
        return response

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="AsphaltRepairs")

    template_name = "bollards.html"
    context = {"title": title,
               "crumb_1_link":crumb_1_link,
               "crumb_1":crumb_1,
               "crumb_2":crumb_2,
               "breadcrumbs_title":breadcrumbs_title,
               "breadcrumbs_title": breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "form" : form,
               "date": date,}
    return render(request, template_name, context)

def about_page(request):
    title = "ABOUT CRUSADER CONCRETE"
    breadcrumbs_title = "About Us"
    meta_title = 'About Us | Crusader Concrete'
    meta_description = "Crusader Concrete is an Ottawa based commercial and residential concrete contractor \
                        founded in 2013. We specialeze in decorative coloured and stamped concrete."
    meta_keywords = "crusader Concrete ottawa, crusader Concrete, crusader Concrete inc"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/about/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "About"
    crumb_1 = "About"

    template_name = "about.html"
    context = {"title": title,
               "crumb_1":crumb_1,
               "breadcrumbs_title":breadcrumbs_title,
               "breadcrumbs_title": breadcrumbs_title,
               "canonical":canonical,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               'og_image' : og_image,
               'og_type' : og_type,
               "date": date,} 
    return render(request, template_name, context)

def careers_page(request):
    title = "OTTAWA CONSTRUCTION JOBS"
    meta_title = 'Ottawa Construction Jobs | Careers With Crusader Concrete'
    meta_description = "Crusader has been employing people in the construction industry since 2013. \
                        We pride ourselves on providing a professional, rewarding and fun environment."
    meta_keywords = "ottawa construction jobs, construction jobs ottawa, equipment operator job ottawa, \
                     landscaping jobs ottawa, construction careers ottawa, construction foreman job ottawa, landscape foreman ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/careers/"
    og_image = "https://mcexcavate.com/static/image/careers/concrete-finisher.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Careers"
    crumb_1 = "Careers"

    template_name = "careers.html"
    context = {"title": title,
               "crumb_1":crumb_1,
               "breadcrumbs_title":breadcrumbs_title,
               "breadcrumbs_title": breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "date": date,}
    return render(request, template_name, context)

def contact_page(request):
    title = "CONTACT US"
    breadcrumbs_title = "Contact Us"
    meta_title = 'Contact Us | Crusader Concrete'
    meta_description = "Contact Us - Phone: 613-608-7722, Email: info@crusaderconcrete.ca or send a message \
                        through one of our forms. Visit our website for more information..."
    meta_keywords = ""
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/contact/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    breadcrumbs_title = "Contact"
    crumb_1 = "Contact"


    form = _build_form(ContactPageContactForm, request)
    response = _process_contact_form_submission(request, form, breadcrumbs_title, "/contact/#contactform")
    if response:
        return response

    template_name = "contact.html"
    context = {
               "title": title, 
               "form": form,
               "crumb_1":crumb_1,
               "breadcrumbs_title":breadcrumbs_title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               'og_image' : og_image,
               'og_type' : og_type,
               "date": date,}    
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
        meta_title = 'Dashboard | Crusader Concrete Inc.'
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
                  "date": date,} 

        return context

def asphalt_page(request):
    title = "ASPHALT DRIVEWAY PAVING OTTAWA"
    meta_title = 'Asphalt Driveway Paving Ottawa'
    meta_description = "Crusader Concrete provides asphalt driveway paving in Ottawa to residential \
                        and commercial clients. We have been one of Ottawa's leading asphalt paving companies since 2013."
    meta_keywords = "driveway paving ottawa, ottawa driveway paving, asphalt driveway paving ottawa, ottawa asphalt driveway paving,\
                     ottawa asphalt driveways, asphalt driveways ottawa, ottawa paving, paving ottawa, driveway paving,\
                     asphalt ottawa, ottawa asphalt,"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/asphalt-paving/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    form = ServicePageContactForm(request.POST or None)
    form = _process_plain_lead_form_submission(request, form, "Asphalt Lead | Asphalt Page")

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
               'og_type' : og_type,
               "date": date,}
    return render(request, template_name, context)

def asphalt_repairs_page(request):
    title = "ASPHALT REPAIRS OTTAWA"
    meta_title = 'Asphalt Repairs Ottawa'
    meta_description = "Crusader Concrete does asphalt repairs including ramps, pathces and pot holes. \
                        Since 2013 we have done residential, commercial and government contracts"
    meta_keywords = "ottawa asphalt repairs, asphalt repairs ottawa, asphalt repairs"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/asphalt-repairs/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    form = ServicePageContactForm(request.POST or None)
    form = _process_plain_lead_form_submission(request, form, "Asphalt Repairs Lead | Asphalt Repairs Page")

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
               'og_type' : og_type,
               "date": date,}
    return render(request, template_name, context)

def interlock_page(request):
    title = "INTERLOCK OTTAWA"
    breadcrumbs_title = "Interlock"
    meta_title = 'Ottawa Interlock | Crusader Concrete'
    meta_description = "Crusader Concrete produces high quality interlock and hardscape projects to commercial, \
                        residential and government clients in Ottawa."
    meta_keywords = "ottawa interlock, interlock ottawa, interlock pathways ottawa, ottawa interlock patio, \
                     interlock driveway, ottawa interlock repair, "
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/interlock/"
    og_image = "https://mcexcavate.com/static/image/interlock/black with grey border interlock front step and walkway.jpg"
    og_type = "website"
    date = datetime.datetime.now()

    if request.method == 'POST' and request.FILES.get('images'):
        form = ServicePageContactForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract the form data
            form_data = form.cleaned_data
            images = request.FILES.getlist('images')

            # save the uploaded images after validating they are images and max of 5
            file_paths = handle_uploaded_files(images, request)

            if file_paths:
                # Send the uploaded images and form data via email
                send_email_with_attachments(form_data, file_paths, breadcrumbs_title)
                messages.success(request, f"Thank you for contacting us {form_data['name']}. We will get back to you quickly about your {form_data['service']} project.")
                form = ServicePageContactForm()
                return HttpResponseRedirect("/interlock/")

            else:
                # If files are not valid or failed validation, we don't proceed
                return HttpResponseRedirect("/interlock/")

    else:
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
               "breadcrumbs_title": breadcrumbs_title,
               "date": date,}
    return render(request, "interlock.html", context)

def re_sodding_page(request):
    title = "SOD INSTALLATION OTTAWA"
    breadcrumbs_title = "Sod Installation"
    meta_title = "Sod Installation Ottawa | Crusader Concrete"
    meta_description = "Crusader Concrete has been providing sod installation in Ottawa since 2013. \
                        We use high quality top soil and make sure the lawn is perfectly graded before laying sod."
    meta_keywords = "sod installation ottawa, ottawa sod installation, ottawa sod install, sod install ottawa, \
                     re-sodding ottawa, ottawa re-sodding, re-sodding, sod installation,"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/sod-installation/"
    og_image = "https://mcexcavate.com/static/image/sod/1_sod_gallery.jpg"
    og_type = "website"
    date = datetime.datetime.now()

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

    if request.method == 'POST' and request.FILES.get('images'):
        form = ServicePageContactForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract the form data
            form_data = form.cleaned_data
            images = request.FILES.getlist('images')

            # save the uploaded image after validating they are images and max of 5
            file_paths = handle_uploaded_files(images, request)

            if file_paths:
                # Send the uploaded images and form data via email
                send_email_with_attachments(form_data, file_paths)
                messages.success(request, f"Thank you for contacting us {form_data['name']}. We will get back to you quickly about your {form_data['service']} project.")
                form = ServicePageContactForm()
                return HttpResponseRedirect("/sod-installation/")

            else:
                # If files are not valid or failed validation, we don't proceed
                return HttpResponseRedirect("/sod-installation/")

    else:
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
               "breadcrumbs_title": breadcrumbs_title,
               "date": date,}
    return render(request, template_name, context)


def concrete_success_page(request):
    title = "Thank you! \
             You are one step closer to becoming another happy customer!"
    meta_title = 'Thank you for contacting us! -Crusader Concrete'
    meta_description = "Thank you for contacting us about your stamped concrete project! \
                        We will be in touch soon to answer your questions or set up an estimate."
    meta_keywords = ""
    meta_robots = "noindex, nofollow" 
    canonical = "https://mcexcavate.com/concrete/success/"
    date = datetime.datetime.now()
      
    template_name = "concrete-success.html"
    context = {"title": title,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "canonical":canonical,
               "date": date,}
    return render(request, template_name, context) 
