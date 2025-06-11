from rest_framework import serializers
from accounts.models import CustomUser
from books.models import Book
from social.models import Like, Comment
from social.serializers import CommentTreeSerializer

class BookMiniSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model  = Book
        fields = ("id", "title", "author", "likes", "created")

class ProfileSerializer(serializers.ModelSerializer):
    total_likes  = serializers.IntegerField(read_only=True)
    books_shared = serializers.IntegerField(read_only=True)
    books        = BookMiniSerializer(source="books.all", many=True, read_only=True)

    class Meta:
        model  = CustomUser
        fields = ("id", "name", "profile_photo", "total_likes", "books_shared", "books")


class BookOwnerDetailSerializer(serializers.ModelSerializer):
    likes    = serializers.IntegerField(source="likes.count", read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model  = Book
        fields = ("id", "title", "author", "description",
                  "pdf_content", "likes", "comments", "created")

    def get_comments(self, obj):
        roots = obj.comments.filter(parent__isnull=True).select_related("user")
        return CommentTreeSerializer(roots, many=True).data
