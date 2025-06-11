from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

def pdf_validator(file):
    if not file.name.lower().endswith(".pdf"):
        raise ValidationError("File must be a PDF.")
    if file.content_type != "application/pdf":
        raise ValidationError("Invalid MIME type; only PDFs allowed.")

class Book(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="books",
        on_delete=models.CASCADE,
    )
    title        = models.CharField(max_length=150)
    author       = models.CharField(max_length=100)
    description  = models.TextField(blank=True)
    pdf_content  = models.FileField(upload_to="books/", validators=[pdf_validator])
    created      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self): return self.title
