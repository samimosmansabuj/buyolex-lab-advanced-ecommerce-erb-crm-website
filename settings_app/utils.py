from django.core.files.storage import default_storage
from django.utils.text import slugify


def image_delete_os(picture):
    if picture and default_storage.exists(picture.name):
        default_storage.delete(picture.name)
        return True

def previous_image_delete_os(old_picture, new_picture):
    if old_picture and old_picture != new_picture and default_storage.exists(old_picture.name):
        default_storage.delete(old_picture.name)
        return True


def generate_unique_slug(model_object, field_value, old_slug=None):
    slug = slugify(field_value)
    if slug != old_slug:
        unique_slug = slug
        num = 1
        while model_object.objects.filter(slug=unique_slug).exists():
            if unique_slug == old_slug:
                return old_slug
            unique_slug = f'{slug}-{num}'
            num+=1
        return unique_slug
    else:
        return old_slug


