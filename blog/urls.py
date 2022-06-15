from django.contrib.auth import views as auth_views
from django.urls import path

from blog.views import Home, SearchView, CategoryView, PostListView, PostDetailView, PhotoDetailView, PostListRest, \
    PostDetailRest, Login, TagIndexView, SignUpView, PwResetView, activate, PwResetDoneView, PwResetConfirmView, \
    PwResetCompleteView, resend_activation, ResendActivaton, ProfileView, Logout

urlpatterns = [
    path('search', SearchView.as_view(), name='search'),
    path('category/<slug:slug>', CategoryView.as_view(), name='category'),
    path('tags/<slug:slug>', TagIndexView.as_view(), name='tagged'),

    path('', Home.as_view(), name='index'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('activate/<slug:uidb64>/<slug:token>/', activate, name='activate'),

    path('reactivate/', resend_activation, name='reactivate'),
    path('reactivation_succesful/', ResendActivaton.as_view(), name='reactivation_successful'),

    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

    path('me/', ProfileView.as_view(), name='profile'),

    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', PwResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PwResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<slug:uidb64>/<slug:token>/', PwResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_done/done/', PwResetCompleteView.as_view(), name='password_reset_complete'),

    path('blog', PostListView.as_view(), name='blog'),
    path('posts/<slug:slug>', PostDetailView.as_view(), name='post-detail'),
    path('photos/<int:pk>', PhotoDetailView.as_view(), name='photo-detail'),

    path('api/blog', PostListRest.as_view(), name='api-blog'),
    path('api/posts/<slug:slug>', PostDetailRest.as_view(), name='api-post-detail'),
]
