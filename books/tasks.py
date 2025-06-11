from celery import shared_task
from .models import Book
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()

@shared_task(bind=True)
def bulk_upload_books(self, user_id, books_data):
    user = User.objects.get(pk=user_id)
    ids = []

    for data in books_data:
        with open(data["file_path"], "rb") as f:
            book = Book.objects.create(
                owner=user,
                title=data["title"],
                author=data["author"],
                description=data["description"],
                pdf_content=models.File(f, name=data["file_path"].split("/")[-1]),
            )
            ids.append(book.id)

    return {"created_book_ids": ids}
