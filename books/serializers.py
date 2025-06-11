from rest_framework import serializers
from .models import Book

class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Book
        fields = ("id", "title", "author", "description", "pdf_content")

    # attach the owner automatically
    def create(self, validated):
        return Book.objects.create(owner=self.context["request"].user, **validated)

class BookListSerializer(serializers.ModelSerializer):
    likes_count    = serializers.IntegerField(source="likes.count", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model  = Book
        fields = ("id", "title", "author", "likes_count", "comments_count", "created")

class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Book
        fields = "__all__"
        read_only_fields = ("owner",)
