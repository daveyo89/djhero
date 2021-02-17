from bs4 import BeautifulSoup
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from tinymce import models as tinymce_models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from cloudinary.models import CloudinaryField
from taggit.managers import TaggableManager
from taggit.models import Tag
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=50, blank=True, null=True, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return str(self.email)


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    slug = models.CharField(max_length=60, unique=True, blank=True)
    image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save()

    def get_absolute_url(self, *args, **kwargs):
        return reverse('category', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "Categories"


class Post(models.Model):
    statuses = [
        ('D', 'Draft'),
        ('P', 'Publish')
    ]
    title = models.CharField(max_length=120, blank=True)
    slug = models.CharField(max_length=60, unique=True, blank=True)
    content = tinymce_models.HTMLField()
    status = models.CharField(max_length=1, choices=statuses)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(auto_now=True)
    image = CloudinaryField('image')
    tags = TaggableManager(verbose_name='Tags', blank=True)

    """ Informative name for model """

    def __unicode__(self):
        try:
            public_id = self.image.public_id
        except AttributeError:
            public_id = ''
        return "Photo <%s:%s>" % (self.title, public_id)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save()

    def get_absolute_url(self, *args, **kwargs):
        return reverse('post-update', kwargs={'slug': self.slug})

    def html_to_text(self, *args, **kwargs):
        soup = BeautifulSoup(self.content, features="html.parser")
        text = soup.get_text()
        return text

    def _tags(self):
        return [t for t in self.tags.all()]

    class Meta:
        ordering = ["-date"]


class PostImage(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    images = CloudinaryField('image')
    description = models.CharField(max_length=120, default='', blank=True)

    def __unicode__(self):
        try:
            public_id = self.images.public_id
        except AttributeError:
            public_id = ''
        return "Photo <%s>" % public_id


class PostVideo(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    video_link = models.CharField(max_length=600, default='', blank=True)

    def save(self, *args, **kwargs):
        self.video_link = self.video_link.replace("watch?v=", "embed/")
        return super().save()


class Introduction(models.Model):
    statuses = [
        ('A', 'Active'),
        ('I', 'In Active')
    ]
    title = models.CharField(max_length=120)
    message = tinymce_models.HTMLField()
    status = models.CharField(max_length=1, choices=statuses, default='I')

    def __str__(self):
        return self.title

    def html_to_text(self, *args, **kwargs):
        soup = BeautifulSoup(self.message, features="html.parser")
        text = " ".join(soup.find_all(text=True))
        return text
