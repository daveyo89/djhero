import json
import os
import urllib

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages.views import SuccessMessageMixin, messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.models import Category, Post, PostImage, PostVideo, Introduction, Tag, TaggableManager, CustomUser
from blog.serializers import PostSerializer
from rest_framework import generics
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm
from .tokens import account_activation_token
from django.utils.translation import gettext_lazy as _


class PwResetCompleteView(PasswordResetCompleteView):
    template_name = 'blog/registration/password_reset_complete.html'


class PwResetConfirmView(PasswordResetConfirmView):
    template_name = 'blog/registration/password_reset_confirm.html'


class PwResetView(PasswordResetView):
    template_name = 'blog/registration/password_reset_form.html'


class PwResetDoneView(PasswordResetDoneView):
    template_name = 'blog/registration/password_reset_done.html'


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive, please check your emails."),
    }


class Login(SuccessMessageMixin, LoginView):
    template_name = 'blog/login.html'
    success_message = 'Login successful!'
    authentication_form = CustomAuthenticationForm


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = 'blog/register.html'
    success_url = reverse_lazy('index')
    form_class = UserRegisterForm
    success_message = 'Your profile was created successfully'
    extra_context = {'google_site_key': os.environ.get('CAPTCHA_SITE')}

    def form_valid(self, form):
        """ Begin reCAPTCHA validation """
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': os.environ.get('CAPTCHA_SECRET'),
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        """ End reCAPTCHA validation """
        if result['success']:
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(self.request)
            mail_subject = f'Activate your account at {current_site.name}.'
            message = render_to_string('blog/acc_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(self.request, message='Please confirm your email address to complete the registration!')

            # user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password1'], )
            # login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect(reverse('login'))
        else:
            messages.error(self.request, 'Invalid reCAPTCHA. Please try again.')
            return HttpResponseRedirect(reverse('signup'))


class Home(LoginRequiredMixin, ListView):
    model = Introduction
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["intro"] = Introduction.objects.filter(status="A")
        if context["intro"]:
            context['message'] = context['intro'][0].get_message_as_markdown()

        return context


class SearchView(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = "posts"
    template_name = "blog/search.html"

    def get_queryset(self):
        query = self.request.GET['query']
        title_queryset = Post.objects.filter(status="P", title__icontains=query)
        author_queryset = Post.objects.filter(status="P", author__username__icontains=query)
        date_queryset = Post.objects.filter(status="P", date__icontains=query)
        content_queryset = Post.objects.filter(status="P", content__icontains=query)
        queryset = title_queryset.union(content_queryset).union(author_queryset).union(date_queryset)
        return queryset


class CategoryView(LoginRequiredMixin, ListView):
    model = Category
    context_object_name = "posts"
    paginate_by = 10
    template_name = "blog/category.html"
    queryset = Post.objects.get_queryset()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CategoryView, self).get_context_data()
        paginator = Paginator(self.queryset, self.paginate_by)
        page = self.request.GET.get('page')
        context['category'] = self.category
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context['posts'] = posts
        return context

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.request.resolver_match.kwargs.get('slug'))
        return Post.objects.filter(status='P', category=self.category).order_by('-date')


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = "posts"
    template_name = "blog/blog.html"
    paginate_by = 6
    queryset = Post.objects.filter(status="P")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['categories'] = Category.objects.filter(post__status='P').annotate(post_count=Count('post'))

        paginator = Paginator(self.queryset, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context['posts'] = posts
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    context_object_name = "post"
    template_name = "blog/post_detail.html"
    queryset = Post.objects.filter(status="P")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        post = self.get_object()
        context['tags'] = post._tags()
        context['previous_post'] = Post.objects.filter(id__lt=post.id, category=post.category).order_by('-id').first()
        context['next_post'] = Post.objects.filter(id__gt=post.id, category=post.category).order_by('id').first()
        context['photos'] = PostImage.objects.filter(post=post)
        context['videos'] = PostVideo.objects.filter(post=post)
        return context


class TagIndexView(LoginRequiredMixin, ListView):
    template_name = 'blog/category.html'
    model = Post
    context_object_name = 'tags'

    paginate_by = 6
    queryset = Post.objects.get_queryset()

    def get_queryset(self):
        return Post.objects.filter(tags__slug=self.kwargs.get('slug'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TagIndexView, self).get_context_data()
        paginator = Paginator(self.queryset, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context['posts'] = posts
        return context


class PhotoDetailView(LoginRequiredMixin, DetailView):
    model = PostImage
    context_object_name = "photo"
    template_name = "blog/photo_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        photo = self.get_object()

        context["photo"] = photo
        return context


class PostListRest(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostDetailRest(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'
    queryset = Post.objects.all()
    serializer_class = PostSerializer


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, message='Successful activation!')
        # return redirect('home')
        return HttpResponseRedirect(reverse('index'))
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')
