from django.urls import path
#from . import views
from.views import HomeView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, CommentCreateView

# URL patterns for blog app
urlpatterns = [
    #path('', views.home, name='home'),
    path('', HomeView.as_view(), name='home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_details'),
    path('post_new/', PostCreateView.as_view(), name='post_new'),
    path('post/edit/<int:pk>/', PostUpdateView.as_view(), name='post_update'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/comment/', CommentCreateView.as_view(), name='comment_new'),
]
