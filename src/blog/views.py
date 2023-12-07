from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
#from django.contrib.sitemaps import Sitemap



# Create your views here.
from .models import BlogPost
from .forms import BlogPostModelForm

@staff_member_required
def blog_post_create_view(request):
    my_title = 'New Blog Post'
    meta_robots = "noindex, nofollow"

    form = BlogPostModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        print("form is valid")
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        form = BlogPostModelForm()
        messages.success(request, f"Your new blog has been posted.")

    template_name = 'blog/create.html'
    context = {'title': my_title, 
               'form': form, 
               "meta_robots":meta_robots}

    return render (request , template_name, context)  

def blog_post_list_view(request):
    title = 'McExcavate Construction Blog'
    meta_title = 'Ottawa Construction Blog | McExcavate'
    meta_robots = "index, follow"
    #og_image = blog_post.img.url
    og_type = "website"

    blogs = BlogPost.objects.all().published()

    meta_description = "Read about various landscaping topics here on our blog. We've got some useful information about concrete, interlock and much more..."
    meta_keywords = ['ottawa bitcoin blog',
                'bitcoin blog ottawa',
                'canada bitcoin blog',
                'bitcoin blog canada']
                
    template_name = 'blog/blog.html'
    context = {'object_list':blogs,
               'title':title,
               "meta_robots":meta_robots,
               'meta_title': meta_title,
               'meta_description' : meta_description,
               'meta_keywords': meta_keywords}

    return render (request , template_name, context) 

def blog_post_detail_view(request, slug):
    blogs = BlogPost.objects.all().published()
    blog_post = get_object_or_404(BlogPost, slug=slug)
    og_image = blog_post.image.url
    og_type = "article"

    meta_title = blog_post.title
    meta_description = (blog_post.content[:147]) + '...'
    meta_keywords = []
    meta_robots = "index, follow"

    template_name = 'blog/detail.html'
    description = 'Canadian Bitcoin Blog - '
    keywords = [blog_post.title]
                
    context = {'og_image' : og_image,
               'og_type' : og_type,
               'blog_post' : blog_post, 
               'object_list':blogs,
               "meta_description":meta_description,
               "meta_robots":meta_robots,
               "meta_keywords":meta_keywords,
               "meta_title":meta_title}

    return render (request , template_name, context)    

@staff_member_required
def blog_post_update_view(request, slug):
    obj = get_object_or_404(BlogPost, slug=slug)
    form = BlogPostModelForm(request.POST or None, request.FILES or None, instance=obj)
    meta_robots = "noindex, nofollow"

    # if request.method == 'POST':
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request, f"This blog post has been updated.")
    # else:
    #     form = BlogPostModelForm()

    if form.is_valid():
        form.save()
        messages.success(request, f"This blog post has been updated.")

    template_name = 'blog/update.html'
    context = {'form' : form, 
               'title':f"Editing: {obj.title}",
               "meta_robots":meta_robots,}

    return render (request , template_name, context)    

@staff_member_required
def blog_post_delete_view(request, slug):
    obj = get_object_or_404(BlogPost, slug=slug)
    meta_robots = "noindex, nofollow" 

    template_name = 'blog/delete.html'
    if request.method == "POST":
        obj.delete()
        return redirect('/blog')
    context = {'object':obj, 
               "meta_robots":meta_robots,}
    return render (request , template_name, context)

# class blog_sitemap(Sitemap):
#     changefreq = "daily"
#     priority = 1.0

#     def items(self):
#         return BlogPost.objects.all()

#     def lastmod(self, obj):
#         return obj.publish_date



