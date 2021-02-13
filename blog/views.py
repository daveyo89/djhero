from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.models import Category, Post, PostImage, PostVideo, Introduction, Tag, TaggableManager
from blog.serializers import PostSerializer
from rest_framework import generics
from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin


def login(request):
    return render(request, 'blog/index.html')


class Home(ListView):
    model = Introduction
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["intro"] = Introduction.objects.filter(status="A")
        if context["intro"]:
            context['message'] = context['intro'][0].html_to_text()

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

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context['posts'] = posts
        return context

    def get_queryset(self):
        category = Category.objects.get(slug=self.request.resolver_match.kwargs.get('slug'))
        return Post.objects.filter(status='P', category=category).order_by('-date')


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

