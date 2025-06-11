from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Like, Comment
from notifications.models import Notification

layer = get_channel_layer()

def _notify(recipient, actor, verb, book, extra_data=None):
    n = Notification.objects.create(
        recipient=recipient, actor=actor, verb=verb, book=book
    )
    async_to_sync(layer.group_send)(
        f"user_{recipient.id}",
        {
            "type": "notification",
            "data": {
                "id": n.id,
                "actor": actor.name or actor.email,
                "verb": verb,
                "book_title": book.title,
                **(extra_data or {}),
            },
        },
    )

@receiver(post_save, sender=Like)
def like_notification(sender, instance, created, **kwargs):
    if not created: return
    if instance.book.owner != instance.user:
        _notify(instance.book.owner, instance.user, "liked", instance.book)

@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    if not created: return
    if instance.book.owner != instance.user:
        _notify(instance.book.owner, instance.user, "commented on", instance.book,
                extra_data={"comment": instance.content[:80]})
