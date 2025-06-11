from rest_framework import serializers
from .models import FriendRequest, Message, Friendship

# ── Friend Request ──────────────────────────
class FriendRequestSerializer(serializers.ModelSerializer):
    from_name = serializers.CharField(source="from_user.name", read_only=True)

    class Meta:
        model  = FriendRequest
        fields = ("id", "from_user", "to_user", "from_name", "status", "created")
        read_only_fields = ("id", "from_user", "status", "created")

# ── Friendship List ─────────────────────────
class FriendSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="other(request_user).name", read_only=True)

    class Meta:
        model  = Friendship
        fields = ("id", "name",)

# ── Messaging ───────────────────────────────
class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.name", read_only=True)

    class Meta:
        model  = Message
        fields = ("id", "sender", "sender_name", "receiver", "content", "created", "is_read")
        read_only_fields = ("id", "sender", "sender_name", "created", "is_read")
