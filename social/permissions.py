from rest_framework.permissions import BasePermission

class CannotLikeOwnBook(BasePermission):
    message = "You can't like your own book."
    def has_permission(self, request, view):
        book = view.get_object()
        return book.owner != request.user
