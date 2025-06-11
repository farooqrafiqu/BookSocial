import json
from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import FileResponse
from .models import Book
from .serializers import (
    BookCreateSerializer, BookListSerializer, BookDetailSerializer,
)
from .permissions import IsOwnerOrReadOnly
from .tasks import bulk_upload_books
import tempfile, os

from social.models import Like, Comment
from social.serializers import (
    LikeSerializer, CommentCreateSerializer, CommentTreeSerializer
)
from social.permissions import CannotLikeOwnBook

class BookViewSet(viewsets.ModelViewSet):
    """
    list           /api/books/
    create         /api/books/
    retrieve       /api/books/{id}/
    read (file)    /api/books/{id}/read/
    batch-upload   /api/books/batch/
    """
    queryset = Book.objects.select_related("owner")
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return BookCreateSerializer
        elif self.action == "list":
            return BookListSerializer
        return BookDetailSerializer

    def get_permissions(self):
        auth_only = (                      
            "create", "batch_upload", "read",
            "like", "unlike", "comments",
        )
        if self.action in auth_only:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:                             
            self.permission_classes = [AllowAny]
        return super().get_permissions()


    @action(detail=True, methods=["get"], url_path="read")
    def read(self, request, pk=None):
        """Return the raw PDF (requires auth)."""
        book = self.get_object()
        return FileResponse(book.pdf_content.open("rb"), content_type="application/pdf")

    @action(detail=False, methods=["post"], url_path="batch")
    def batch_upload(self, request):
        """
        Accept multiple PDFs in one request; handled asynchronously.
        Send as multipart/form-data:
          files:   list of files (pdf)
          meta:    JSON list with {'title','author','description','filename'}
        """
        files = request.FILES.getlist("files")
        meta  = request.data.get("meta", "[]")
        try:
            meta = json.loads(meta)
        except ValueError:
            return Response({"detail": "meta must be valid JSON"}, status=400)

        if len(files) != len(meta):
            return Response({"detail": "files and meta length mismatch"}, status=400)

        tmp_dir = tempfile.mkdtemp()
        books_data = []

        for file_obj, meta_info in zip(files, meta):
            path = os.path.join(tmp_dir, file_obj.name)
            with open(path, "wb") as dst:
                for chunk in file_obj.chunks():
                    dst.write(chunk)

            books_data.append({
                "title": meta_info.get("title"),
                "author": meta_info.get("author"),
                "description": meta_info.get("description", ""),
                "file_path": path,
            })

        task = bulk_upload_books.delay(request.user.id, books_data)
        return Response({"detail": f"{len(files)} books queued", "task_id": task.id},
    status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, CannotLikeOwnBook])
    def like(self, request, pk=None):
        book = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, book=book)
        if not created:
            return Response({"detail": "Already liked"}, status=400)
        return Response(LikeSerializer(like).data, status=201)

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        book = self.get_object()
        deleted, _ = Like.objects.filter(user=request.user, book=book).delete()
        if deleted:
            return Response(status=204)
        return Response({"detail": "You haven't liked this book"}, status=400)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def likes(self, request, pk=None):
        book = self.get_object()
        qs = book.likes.select_related("user")
        return Response(LikeSerializer(qs, many=True).data)

    # ----- COMMENTS -----
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        """POST = add comment   GET = list comments"""
        book = self.get_object()
        if request.method == "POST":
            s = CommentCreateSerializer(data=request.data, context={"request": request, "book": book})
            s.is_valid(raise_exception=True)
            s.save()
            return Response({"detail": "Comment added"}, status=201)

        root_comments = book.comments.filter(parent__isnull=True).select_related("user")
        data = CommentTreeSerializer(root_comments, many=True).data
        return Response(data)

    