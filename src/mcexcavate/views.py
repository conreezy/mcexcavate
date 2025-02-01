from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse
from django.template.loader import get_template
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
import requests
from requests import Request, Session
import json
from project.models import SodEstimate, PavingEstimate
from .forms import ServicePageContactForm, ContactPageContactForm, SodPriceForm, PavingPriceForm
from blog.models import BlogPost
import os
from PIL import Image
from django.core.exceptions import ValidationError

MAX_UPLOAD_IMAGES = 5  # Limit to 5 images

def is_image(image):
    try:
        img = Image.open(image)
        img.verify()  # This will raise an error if the file is not a valid image
        return True
    except (IOError, SyntaxError):
        return False

def handle_uploaded_files(images, request):
    # Check if the number of files is within the allowed limit
    if len(images) > MAX_UPLOAD_IMAGES:
        messages.error(request, f"Error: Only {MAX_UPLOAD_IMAGES} images are allowed. You tried to upload {len(images)}.")
        return None

    # Define a directory where you want to save the uploaded files
    upload_dir = "static/image/formuploads/"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Save the uploaded file to the directory
    file_paths = []
    for i in images:
        print(f"Processing file: {i.name}")  # Debugging statement
        if not is_image(i):
            messages.error(request, f"The file {i.name} is not a valid image.")
            return False

        file_path = os.path.join(upload_dir, i.name)
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in i.chunks():
                    destination.write(chunk)
            file_paths.append(file_path)
            print(f"Saved file: {file_path}")  # Debugging statement
        except Exception as e:
            print(f"Failed to save file {i.name}: {e}")  # Debugging statement
            return None

    return file_paths if file_paths else None

def send_email_with_attachments(form_data, file_paths):
    # Construct the email body with the form data
    email_body = f"""
    Name: {form_data['name']}
    Email: {form_data['email']}
    Phone: {form_data['phone']}
    Address: {form_data['address']}
    Marketing: {form_data['marketing']}
    Service: {form_data['service']}
    Message: {form_data['content']}
    
    """

    # Create the email message
    email = EmailMessage(
        subject=f"{form_data['service']} Lead | Contact Page",
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=['mcexcavate.ottawa@gmail.com'],
    )

    # Attach images only if there are valid files
    if file_paths:
        for file_path in file_paths:
            try:
                print(f"Attaching file: {file_path}")  # Debugging statement
                with open(file_path, 'rb') as attachment:
                    email.attach(os.path.basename(file_path), attachment.read(), 'application/octet-stream')
            except Exception as e:
                print(f"Error attaching file {file_path}: {e}")

    # Attach each Image
    # for file_path in file_paths:
    #     with open(file_path, 'rb') as attachment:
    #         email.attach(os.path.basename(file_path), attachment.read(), 'application/octet-stream')
    
    # Send the email
    email.send()
    print("Email sent successfully!")  # Debugging statement

def home_page(request):
    title = "Crusader Concrete"
    meta_title = "Crusader Concrete | Ottawa Concrete Contractor"
    meta_description =  "Discover Ottawa's top stamped concrete solutions for patios, driveways, and walkways. \
                         Enhance your home with durable, stylish designs."
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
    meta_title = 'Our Services | Crusader Concrete'
    meta_description = "We are stamped concrete experts, we also do plain concrete, steps, sidewalks and curbs. \
                        Additionaly we do sod installation, interlock and excavation"
    meta_keywords = "Crusader Concrete services"
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
    meta_title = 'Ottawa Excavation Services | Crusader Concrete'
    meta_description = "Crusader Concrete provides Ottawa Excavation services to commercial, residential \
                        and government clients. One of Ottawa's leading excavation companies since 2013."
    meta_keywords = "ottawa excavation, excavation ottawa, excavating ottawa, ottawa excavating, \
                    excavation services, ottawa excavation services, excavation, excavating"
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
    meta_title = 'Ottawa Interlock | Crusader Concrete'
    meta_description = "Crusader Concrete produces high quality interlock and hardscape projects to commercial, \
                        residential and government clients in Ottawa."
    meta_keywords = "ottawa interlock, interlock ottawa, interlock pathways ottawa, ottawa interlock patio, \
                     interlock driveway, ottawa interlock repair, "
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/interlock/"
    og_image = "https://mcexcavate.com/static/image/interlock/black with grey border interlock front step and walkway.jpg"
    og_type = "website"

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
                send_email_with_attachments(form_data, file_paths)
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
               "breadcrumbs_title": breadcrumbs_title,}
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
               "breadcrumbs_title": breadcrumbs_title,}
    return render(request, template_name, context)

def stamped_concrete_page(request):
    title = "STAMPED CONCRETE OTTAWA"
    breadcrumbs_title = "Stamped Concrete"
    meta_title = 'Stamped Concrete Ottawa | Crusader Concrete'
    meta_description = "Crusader Concrete specializes in stamped concrete in Ottawa. We have been \
                        building stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, stamped concrete, stamped concrete ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    if request.method == 'POST':
        print("Form submission received!")  # Debugging statement
        print(request.FILES)  # This will show if images are being sent
        form = ServicePageContactForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid!")
            # Extract the form data
            form_data = form.cleaned_data
            images = request.FILES.getlist('images')
            print(f"Number of images received: {len(images)}")  # Debugging statement
            # save the uploaded image after validating they are images and max of 5
            file_paths = handle_uploaded_files(images, request) if images else []

            if images and file_paths is None:
                messages.error(request, "One or more uploaded files are invalid. Please upload only valid images.")
                return redirect(request.path)  # Stay on the same page

            # Send email with or without images
            send_email_with_attachments(form_data, file_paths)
            messages.success(request, f"Thank you for contacting us {form_data['name']}. We will get back to you quickly about your {form_data['service']} project.")
            return HttpResponseRedirect("/concrete/") # Redirect on success

        else:
            messages.error(request, "There was an error in your form submission. Please check the fields and try again.")
    else:
        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="Concrete")    
      
    template_name = "stamped_concrete.html"
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
    meta_title = 'Thank you for contacting us! -Crusader Concrete'
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
                return HttpResponseRedirect("/contact/")

            else:
                # If files are not valid or failed validation, we don't proceed
                return HttpResponseRedirect("/contact/")

    else:
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
    meta_description = "Crusader Concrete specializes in stamped concrete in Ottawa. We have been building \
                        stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete-resurfacing/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

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
                return HttpResponseRedirect("/contact/")

            else:
                # If files are not valid or failed validation, we don't proceed
                return HttpResponseRedirect("/contact/")

    else:
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
    meta_description = "Crusader Concrete specializes in stamped concrete in Ottawa. We have been \
                        building stamped concrete patios, walkways and driveways since 2013."
    meta_keywords = "ottawa stamped conrete, concrete ottawa, stamped concrete ottawa, ottawa concrete"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete-sealing/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/sealing-stamped-concrete.jpg"
    og_type = "website"

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
                return HttpResponseRedirect("/contact/")

            else:
                # If files are not valid or failed validation, we don't proceed
                return HttpResponseRedirect("/contact/")

    else:
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
    title = "PLAIN CONCRETE"
    breadcrumbs_title = "Plain Concrete"
    meta_title = 'Ottawa Concrete | Crusader Concrete'
    meta_description = "We build concrete slabs from excavation to forming and pouring. \
                        Commercial and residential. Basement and garage floors, shed pads, hot tub pads..."
    meta_keywords = "conrete slabs, concrete slabs ottawa, ottawa concrete slabs"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/concrete-slabs/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/smoothfinish.jpg"
    og_type = "website"

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
                return HttpResponseRedirect("/contact/")

            else:
                # If files are not valid or failed validation, we don't proceed
                return HttpResponseRedirect("/contact/")

    else:
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
                return HttpResponseRedirect("/contact/")

            else:
                # If files are not valid or failed validation, we don't proceed
                return HttpResponseRedirect("/contact/")

    else:
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

def bollard_page(request):
    title = "SECURITY BOLLARDS"
    breadcrumbs_title = "Bollards"
    meta_title = 'Security Bollards Ottawa | Crusader Concrete'
    meta_description = "Crusader Concrete installs bollards for commercial, residential and government clients. \
                        One of Ottawa's leading installers of bollards since 2013."
    meta_keywords = "ottawa bollards, bollards ottawa, security bollards ottawa, ottawa security bollards"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/bollards/"
    og_image = "https://mcexcavate.com/static/image/bollards/man_bollard11.jpg"
    og_type = "website"

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
                return HttpResponseRedirect("/contact/")

            else:
                # If files are not valid or failed validation, we don't proceed
                return HttpResponseRedirect("/contact/")

    else:
        form = ServicePageContactForm()

    # Blog Posts section
    blogs = BlogPost.objects.filter(service="AsphaltRepairs")

    template_name = "bollards.html"
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

def parging_page(request):
    title = "PARGING"
    breadcrumbs_title = "Parging"
    meta_title = 'Parging Ottawa | Crusader Concrete'
    meta_description = "Crusader Concrete provides parging services to commercial, residential \
                        and government clients. One of Ottawa's leading parging service providers since 2013."
    meta_keywords = "ottawa parging, parging ottawa"
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/parging/"
    og_image = "https://mcexcavate.com/static/image/parging/white_parging.jpg"
    og_type = "website"

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
                return HttpResponseRedirect("/contact/")

            else:
                # If files are not valid or failed validation, we don't proceed
                return HttpResponseRedirect("/contact/")

    else:
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
    meta_title = 'Ottawa Construction Jobs | Careers With Crusader Concrete'
    meta_description = "Crusader has been employing people in the construction industry since 2013. \
                        We pride ourselves on providing a professional, rewarding and fun environment."
    meta_keywords = "ottawa construction jobs, construction jobs ottawa, equipment operator job ottawa, \
                     landscaping jobs ottawa, construction careers ottawa, construction foreman job ottawa, landscape foreman ottawa"
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
    meta_title = 'Contact Us | Crusader Concrete'
    meta_description = "Contact Us - Phone: 613-608-7722, Email: info@crusaderconcrete.ca or send a message \
                        through one of our forms. Visit our website for more information..."
    meta_keywords = ""
    meta_robots = "index, follow"
    canonical = "https://mcexcavate.com/contact/"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"


    if request.method == 'POST':
        form = ContactPageContactForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid!")
            # Extract the form data
            form_data = form.cleaned_data
            images = request.FILES.getlist('images')
            # save the uploaded image after validating they are images and max of 5
            file_paths = handle_uploaded_files(images, request) if images else []

            if images and file_paths is None:
                messages.error(request, "One or more uploaded files are invalid. Please upload only valid images.")
                return redirect(request.path)  # Stay on the same page

            # Send email with or without images
            send_email_with_attachments(form_data, file_paths)
            messages.success(request, f"Thank you for contacting us {form_data['name']}. We will get back to you quickly about your {form_data['service']} project.")
            return HttpResponseRedirect("/concrete/") # Redirect on success

        else:
            messages.error(request, "There was an error in your form submission. Please check the fields and try again.")
    else:
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
                  } 

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
    meta_description = "Crusader Concrete does asphalt repairs including ramps, pathces and pot holes. \
                        Since 2013 we have done residential, commercial and government contracts"
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
        subject = f"Asphalt Repairs Lead | Asphalt Repairs Page"
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