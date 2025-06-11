"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from accounts import views as acc
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from books.views import BookViewSet

urlpatterns = [
    path("api/auth/register/",    acc.RegisterView.as_view()),
    path("api/auth/verify-otp/",  acc.VerifyOTPView.as_view()),
    path("api/auth/login/",       acc.LoginView.as_view()),
    path("api/auth/resend-otp/", acc.ResendOTPView.as_view()),
]


router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")

urlpatterns += [ path("api/", include(router.urls)) ]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

from tasks.views import TaskStatusView
urlpatterns += [
    path("api/tasks/<uuid:task_id>/", TaskStatusView.as_view()),
]

from rest_framework.routers import DefaultRouter
from friends.views import FriendRequestViewSet, FriendListView, MessageViewSet

router = DefaultRouter()
router.register(r"friends/requests", FriendRequestViewSet, basename="friend-req")
router.register(r"messages",        MessageViewSet,       basename="message")

urlpatterns += [
    path("api/friends/", FriendListView.as_view()),
    path("api/", include(router.urls)),
]

from profiles.views import MyProfileView, MyBookDetailView

urlpatterns += [
    path("api/profile/me/",                MyProfileView.as_view()),
    path("api/profile/me/books/<int:book_id>/", MyBookDetailView.as_view()),
]
