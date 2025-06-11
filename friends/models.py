from django.db import models
from django.conf import settings
from django.utils import timezone

# ────────────── Friend Request ──────────────
class FriendRequest(models.Model):
    PENDING  = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    STATUS_CHOICES = [
        (PENDING,  PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_requests",
        on_delete=models.CASCADE,
    )
    to_user   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_requests",
        on_delete=models.CASCADE,
    )
    status   = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created  = models.DateTimeField(auto_now_add=True)
    decision = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("from_user", "to_user")  

    def accept(self):
        self.status   = self.ACCEPTED
        self.decision = timezone.now()
        self.save(update_fields=["status", "decision"])

        Friendship.objects.get_or_create_pair(self.from_user, self.to_user)

    def reject(self):
        self.status   = self.REJECTED
        self.decision = timezone.now()
        self.save(update_fields=["status", "decision"])

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"

# ────────────── Friendship table (symmetrical) ──────────────
class  FriendshipManager(models.Manager):
    def get_or_create_pair(self, user_a, user_b):
        uid1, uid2 = sorted([user_a.id, user_b.id])
        return self.get_or_create(user1_id=uid1, user2_id=uid2)

class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    created = models.DateTimeField(auto_now_add=True)

    objects = FriendshipManager()

    class Meta:
        unique_together = ("user1", "user2")

    def __str__(self):
        return f"{self.user1} ↔ {self.user2}"

    def other(self, me): 
        return self.user2 if me == self.user1 else self.user1

# ────────────── Message ──────────────
class Message(models.Model):
    sender   = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_messages",   on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="received_messages", on_delete=models.CASCADE)
    content  = models.TextField()
    created  = models.DateTimeField(auto_now_add=True)
    is_read  = models.BooleanField(default=False)

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:30]}..."

