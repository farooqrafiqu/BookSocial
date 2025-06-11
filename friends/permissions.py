from rest_framework.permissions import BasePermission
from .models import Friendship

class IsFriend(BasePermission):
    """
    Allow action only if request.user is friends with the given target_user
    (passed in view.get_target_user()).
    """
    message = "Users must be friends."

    def has_permission(self, request, view):
        target = view.get_target_user()
        if target is None:
            return True 
        uid1, uid2 = sorted([request.user.id, target.id])
        return Friendship.objects.filter(user1_id=uid1, user2_id=uid2).exists()
