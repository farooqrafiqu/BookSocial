from django.shortcuts import render
from django.db import models
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import FriendRequest, Friendship, Message
from .serializers import (
    FriendRequestSerializer, FriendSerializer, MessageSerializer
)
from .permissions import IsFriend

User = get_user_model()

# ────────────── Friend Request ViewSet ──────────────
class FriendRequestViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    POST   /api/friends/requests/          (send)
    GET    /api/friends/requests/          (list pending requests for me)
    POST   /api/friends/requests/<id>/accept/
    POST   /api/friends/requests/<id>/reject/
    """
    serializer_class   = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status=FriendRequest.PENDING)

    def perform_create(self, serializer):
        to_user_id = self.request.data.get("to_user")
        if not to_user_id:
            raise serializers.ValidationError({"to_user": "Required"})
        if int(to_user_id) == self.request.user.id:
            raise serializers.ValidationError({"detail": "Cannot friend yourself"})
        if Friendship.objects.filter(
                user1_id=min(self.request.user.id, to_user_id),
                user2_id=max(self.request.user.id, to_user_id)).exists():
            raise serializers.ValidationError({"detail": "Already friends"})

        serializer.save(from_user=self.request.user)

    # accept / reject -----------------
    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request, pk=None):
        fr = self.get_object()
        fr.accept()
        return Response({"detail": "Friend request accepted"}, status=200)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        fr = self.get_object()
        fr.reject()
        return Response({"detail": "Friend request rejected"}, status=200)

# ────────────── Friends List ──────────────
class FriendListView(APIView):
    """
    GET /api/friends/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Friendship.objects.filter(
            models.Q(user1=request.user) | models.Q(user2=request.user)
        )
        
        data = [ {"id": f.id,
                  "friend_id": f.user2.id if f.user1==request.user else f.user1.id,
                  "friend_name": f.user2.name if f.user1==request.user else f.user1.name }
                 for f in qs ]
        return Response(data)

# ────────────── Messaging ──────────────
class MessageViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    POST /api/messages/          (send)
    GET  /api/messages/?friend_id=<id>   (thread with that friend)
    """
    serializer_class   = MessageSerializer
    permission_classes = [IsAuthenticated, IsFriend]

    def get_target_user(self):
        friend_id = self.request.data.get("receiver") or self.request.query_params.get("friend_id")
        return User.objects.filter(id=friend_id).first()

    def get_queryset(self):
        friend_id = self.request.query_params.get("friend_id")
        if not friend_id:
            return Message.objects.none()
        return Message.objects.filter(
            (models.Q(sender=self.request.user, receiver_id=friend_id) |
             models.Q(sender_id=friend_id, receiver=self.request.user))
        )

    def perform_create(self, serializer):
        receiver = get_object_or_404(User, id=self.request.data["receiver"])
        serializer.save(sender=self.request.user, receiver=receiver)

