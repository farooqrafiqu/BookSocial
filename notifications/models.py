from django.db import models

from django.db import models
from django.conf import settings
from books.models import Book

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notifications",
        on_delete=models.CASCADE
    )
    actor   = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    verb    = models.CharField(max_length=20)              # "liked" / "commented"
    book    = models.ForeignKey(Book, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    read    = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)

    def __str__(self): return f"{self.actor} {self.verb} {self.book}"

