from django.db import models
import PIL
from PIL import Image, ExifTags
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


# Create your models here.
class Gallery(models.Model):
    id = models.AutoField(primary_key=True)
    title   = models.CharField(max_length=50, blank=False, null=True)
    image   = models.FileField(upload_to='image/gallery/', blank=False, null=True)
    slug    = models.SlugField(unique=True, blank=False, null=True) 
    description = models.TextField(null=True, blank=False)
    meta_title  = models.CharField(max_length=55, blank=False, null=True)
    meta_keywords  = models.CharField(max_length=160, blank=False, null=True) 

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/gallery/{self.slug}"

    def get_edit_url(self):
        return f"{self.get_absolute_url()}/edit"

    def get_delete_url(self):
        return f"{self.get_absolute_url()}/delete"

    def save(self, *args, **kwargs):
        if not self.id: 

            # open image
            image_ = Image.open(self.image)

            # get & declare width & height
            (width, height) = image_.size
            
            # calculate & declare width to height ratio
            ratio = width / height

           # get & declare exif data
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            
            image_exif = image_._getexif()

            try:
                if image_exif:
                    if image_exif[orientation] == 3:
                        image_=image_.rotate(180, expand=True)
                    elif image_exif[orientation] == 6:
                        image_=image_.rotate(270, expand=True)
                        try:
                            image_=image_.resize(( int(450//ratio), 450), Image.Resampling.LANCZOS)
                        except:
                            pass
                    elif image_exif[orientation] == 8:
                        image_=image_.rotate(90, expand=True)
                        try:
                            image_=image_.resize(( int(450//ratio), 450), Image.Resampling.LANCZOS)
                        except:
                            pass
                    else:
                        image_=image_.resize((800, ( int(800//ratio))), Image.Resampling.LANCZOS)
                else:
                    try:
                        if width > height:
                            image_=image_.resize((800, int(800//ratio)), Image.Resampling.LANCZOS)
                        else:
                            image_=image_.resize((int(800*ratio), 800), Image.Resampling.LANCZOS)
                    except:
                        pass
            except:
                pass

            output = BytesIO()

            #after resize, save it to the output
            image_.save(output, format='JPEG', quality=100)
            output.seek(0)

            #change the imagefield value to be the newley modifed image value
            self.image = InMemoryUploadedFile(output,'FileField', "%s.jpg" %self.image.name.split('.')[0], 'image/gallery/', sys.getsizeof(output), None)


        super(Gallery, self).save()

class GalleryImages(models.Model):
    id = models.AutoField(primary_key=True)
    images = models.FileField(upload_to='image/gallery/', blank=True, null=True)
    alt = models.CharField(max_length=250, blank=True, null=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.id:

            # open image
            image_ = Image.open(self.images)

            # get & declare width & height
            (width, height) = image_.size
            
            # calculate & declare width to height ratio
            ratio = width / height

           # get & declare exif data
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            
            image_exif = image_._getexif()

            try:
                if image_exif:
                    if image_exif[orientation] == 3:
                        image_=image_.rotate(180, expand=True)
                    elif image_exif[orientation] == 6:
                        image_=image_.rotate(270, expand=True)
                        try:
                            image_=image_.resize(( int(450//ratio), 450), Image.Resampling.LANCZOS)
                        except:
                            pass
                    elif image_exif[orientation] == 8:
                        image_=image_.rotate(90, expand=True)
                        try:
                            image_=image_.resize(( int(450//ratio), 450), Image.Resampling.LANCZOS)
                        except:
                            pass
                    else:
                        image_=image_.resize((800, ( int(800//ratio))), Image.Resampling.LANCZOS)
                else:
                    try:
                        if width > height:
                            image_=image_.resize((800, int(800//ratio)), Image.Resampling.LANCZOS)
                        else:
                            image_=image_.resize((int(800*ratio), 800), Image.Resampling.LANCZOS)
                    except:
                        pass
            except:
                pass

            output = BytesIO()

            #after resize, save it to the output
            image_.save(output, format='JPEG', quality=100)
            output.seek(0)

            #change the imagefield value to be the newley modifed image value
            self.images = InMemoryUploadedFile(output,'FileField', "%s.jpg" %self.images.name.split('.')[0], 'image/gallery/', sys.getsizeof(output), None)

            # make alt text the image file name
            alt_text = self.images.url
            alt_text = alt_text.replace('/', '')
            alt_text = alt_text.replace('media', '')
            alt_text = alt_text.replace('image', '')
            alt_text = alt_text.replace('gallery', '')
            alt_text = alt_text.replace('.jpg', '')
            alt_text = alt_text.replace('.JPG', '')
            alt_text = alt_text.replace('.jpeg', '')
            alt_text = alt_text.replace('.JPEG', '')
            alt_text = alt_text.replace('.png', '')
            alt_text = alt_text.replace('.PNG', '')
            self.alt = alt_text

        super(GalleryImages, self).save(*args, **kwargs)