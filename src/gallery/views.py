from django.shortcuts import render
from .models import Gallery, GalleryImages
from .forms import GalleryForm, GalleryImagesForm, GalleryEditForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

@login_required
def gallery_create_view(request):
    title = 'Create New Gallery'
    meta_robots = 'noindex, nofollow'

    if request.method == 'POST':
        gallery_form = GalleryForm(request.POST, request.FILES)
        gallery_images_form = GalleryImagesForm(request.POST, request.FILES)
        images = request.FILES.getlist('images') #field name in model
        if gallery_form.is_valid() and gallery_images_form.is_valid():
            gallery_instance = Gallery.objects.create(**gallery_form.cleaned_data)
            gallery_instance.save()
            for img in images:
                image_instance = GalleryImages(images=img, gallery=gallery_instance)
                image_instance.save()
            gallery_form = GalleryForm()
            gallery_images_form = GalleryImagesForm()
        else:
            print("error not valid")
    else:
        gallery_form = GalleryForm()
        gallery_images_form = GalleryImagesForm()

    template_name  = 'gallery/create.html'
    context = {"title": title, 
              'gallery_form': gallery_form, 
              'gallery_images_form': gallery_images_form,
              "meta_robots":meta_robots}
    return render(request, template_name, context)

def gallery_list_view(request):
    title = "OUR PROJECTS"
    meta_title = 'Our Projects | McExcavate Inc.'
    meta_description = "Visit our projects gallery to see photos of work we have done over the years. Stamped concrete, sodding, and interlock project photos..."
    meta_keywords = "concrete photos, interlock photos, sodding photos"
    meta_robots = "index, follow"
    og_image = "https://mcexcavate.com/static/image/stamped-concrete/stamped_service_link.jpg"
    og_type = "website"

    galleries = Gallery.objects.all()

    template_name = 'gallery/list.html'
    context = {"title": title, 
               'galleries': galleries,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               'og_image' : og_image,
               'og_type' : og_type,}
    return render(request, template_name, context)

def gallery_detail_view(request, slug):
    obj = get_object_or_404(Gallery, slug=slug)
    gallery = list(GalleryImages.objects.filter(gallery=obj)) 
    paginator = Paginator(gallery, 8)

    title = (obj.title) + " Projects"
    meta_title = obj.meta_title
    meta_keywords = obj.meta_keywords
    meta_description = obj.description
    meta_robots = "index, follow"

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    og_image = obj.image.url
    og_type = "website"
    
    template_name = "gallery/detail.html"
    context = {"title": title, 
               "gallery":gallery,
               "obj":obj,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title,
               "page_obj":page_obj,
               "slug":slug,
               'og_image' : og_image,
               'og_type' : og_type,}
    return render(request, template_name, context)

@login_required
def gallery_edit_view(request, slug):
    title = "Edit This Gallery"
    meta_robots = "noindex, nofollow"
    form = GalleryEditForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        form = GalleryEditForm(request.POST or None, request.FILES or None)
        images = request.FILES.getlist('images') #field name in model
        if form.is_valid():
            for img in images:
                image_instance = GalleryImages(images=img, gallery=form.cleaned_data.get('gallery'))
                image_instance.save()

            messages.success(request, f"Your photo(s) have been uploaded.")
            form = GalleryEditForm()
    else:
        form = GalleryEditForm()

    template_name = 'gallery/edit.html'
    context = {"title": title, 
               "meta_robots":meta_robots,
               "form":form,
               "slug":slug}
    return render(request, template_name, context)

@login_required
def gallery_delete_view(request):
    title = "Delete This Gallery"
    meta_robots = "noindex, nofollow"

    template_name = 'gallery/delete.html'
    context = {"title": title, "meta_robots":meta_robots}
    return render(request, template_name, context)