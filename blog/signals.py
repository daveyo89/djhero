import cloudinary.uploader
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from .models import PostImage


@receiver(pre_delete, sender=PostImage)
def photo_delete(sender, instance, **kwargs):
    cloudinary.uploader.destroy(instance.images.public_id)


@receiver(post_save, sender=PostImage)
def my_callback(sender, instance, *args, **kwargs):
    cloudinary.uploader.rename(instance.images.public_id, instance.post.title + "/" + instance.images.public_id)
    PostImage.objects.filter(id=instance.id).update(images=instance.post.title + "/" + instance.images.public_id)
