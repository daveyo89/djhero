from django.urls import path, include
from django.contrib.auth import views as auth_views
from blog.views import Home, SearchView, CategoryView, PostListView, PostDetailView, PhotoDetailView, PostListRest, PostDetailRest, login

urlpatterns = [
    path('search', SearchView.as_view(), name='search'),
    path('category/<slug:slug>', CategoryView.as_view(), name='category'),

    path('', Home.as_view(), name='index'),
    path('login/', login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('blog', PostListView.as_view(), name='blog'),
    path('posts/<slug:slug>', PostDetailView.as_view(), name='post-detail'),
    path('photos/<int:pk>', PhotoDetailView.as_view(), name='photo-detail'),

    path('api/blog', PostListRest.as_view(), name='api-blog'),
    path('api/posts/<slug:slug>', PostDetailRest.as_view(), name='api-post-detail'),
]
