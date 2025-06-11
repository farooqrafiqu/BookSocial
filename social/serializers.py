from rest_framework import serializers
from .models import Like, Comment

# ----- Likes -----
class LikeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model  = Like
        fields = ("id", "user", "user_name", "created")
        read_only_fields = ("id", "user", "created")


# ----- Comments -----
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Comment
        fields = ("id", "content", "parent")

    def validate(self, data):
        book = self.context["book"]
        user = self.context["request"].user

        if book.owner == user and data.get("parent") is None:
            raise serializers.ValidationError("You can't comment on your own book.")
        return data

    def create(self, validated):
        book = self.context["book"]
        return Comment.objects.create(
            user=self.context["request"].user,
            book=book,
            **validated
        )

class CommentTreeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    replies   = serializers.SerializerMethodField()

    class Meta:
        model  = Comment
        fields = ("id", "user", "user_name", "content", "created", "replies")

    def get_replies(self, obj):
        return CommentTreeSerializer(obj.replies.all(), many=True).data
