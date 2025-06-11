from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.db import models

class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email          = models.EmailField(unique=True)
    phone          = models.CharField(max_length=20, unique=True)
    name           = models.CharField(max_length=120, blank=True)
    profile_photo  = models.ImageField(upload_to="avatars/", blank=True, null=True)
    date_joined    = models.DateTimeField(auto_now_add=True)
    last_login_at  = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)
    is_verified   = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["phone"]

    def __str__(self): return self.email
