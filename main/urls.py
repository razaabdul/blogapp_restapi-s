from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *
router=DefaultRouter()

router.register(r"user", UsersView, basename="user")
# router.register(r"blogview", BlogViewSet, basename="BlogViewSet")
urlpatterns=[
    # path('register/',registerview,base='register'),
    # path('login/',LoginView.as_view(),name='login'),

    path('blog/',blogview.as_view(),name='blog'),
    path('blog/<str:pk>/',blogview.as_view(),name='blog'),
    path('blogcomment/<str:blog_uuid>/',commentview.as_view(),name='blogcomment'),
    path('like/<str:pk>/',likeview.as_view(),name='like'),
    path('blog/date/<str:month_name>/', FilterBlogsByMonth.as_view(), name='filter_blogs_by_month'),
    path('profile/', userprofile.as_view(), name='user_profile'),
    path('logout/',LogoutView.as_view(),name='logout'),

]
urlpatterns+=router.urls  # add the outside url of router
