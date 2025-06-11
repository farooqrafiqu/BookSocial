from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.shortcuts import get_object_or_404
from books.models import Book
from social.models import Like
from .serializers import ProfileSerializer, BookOwnerDetailSerializer
from accounts.models import CustomUser

class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = (
            CustomUser.objects
            .filter(pk=request.user.pk)
            .annotate(
                total_likes=Count("books__likes"),
                books_shared=Count("books"),
            )
            .prefetch_related("books")
            .get()
        )
        return Response(ProfileSerializer(user).data)

    def patch(self, request):
        """
        PATCH /api/profile/me/
        Accepts: { "name": "...", "profile_photo": <file> }
        """
        user = request.user
        if "name" in request.data:
            user.name = request.data["name"]
        if "profile_photo" in request.FILES:
            user.profile_photo = request.FILES["profile_photo"]
        user.save()
        return Response({"detail": "Profile updated"})


class MyBookDetailView(APIView):
    """
    GET /api/profile/me/books/<book_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id):
        book = get_object_or_404(
            Book.objects.filter(owner=request.user),
            pk=int(book_id)
        )
        data = BookOwnerDetailSerializer(book).data
        return Response(data)
