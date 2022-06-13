import cloudinary.uploader
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver, Signal

from .models import PostImage, CustomUser
from .telegram_bot import telegram_bot_sendtext


@receiver(post_save, sender=CustomUser)
def telegram_user_registered(sender, instance, created, **kwargs):
    if created:
        telegram_bot_sendtext(instance.email + " has registered to your site!")


user_activated = Signal(providing_args=["msg"])


@receiver(user_activated)
def telegram_inactive(sender, msg, **kwargs):
    telegram_bot_sendtext(msg)


@receiver(pre_delete, sender=PostImage)
def photo_delete(sender, instance, **kwargs):
    cloudinary.uploader.destroy(instance.images.public_id)


@receiver(post_save, sender=PostImage)
def my_callback(sender, instance, *args, **kwargs):
    cloudinary.uploader.rename(instance.images.public_id, instance.post.title + "/" + instance.images.public_id)
    PostImage.objects.filter(id=instance.id).update(images=instance.post.title + "/" + instance.images.public_id)
