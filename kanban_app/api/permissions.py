"""Access control of the kanban_app."""
from rest_framework.permissions import BasePermission


class IsBoardOwnerOrMember(BasePermission):
    """Allows access only to the board's owner or its members.

    Deleting a board is restricted to the owner.
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        is_member = request.user in obj.members.all()
        if request.method == "DELETE":
            return is_owner
        return is_owner or is_member


class IsTaskBoardMember(BasePermission):
    """Allows task access only to members (or the owner) of the board.

    Deleting a task is restricted to its assignee or the board owner.
    """

    def has_object_permission(self, request, view, obj):
        board = obj.board
        is_owner = board.owner == request.user
        is_member = request.user in board.members.all()
        if request.method == "DELETE":
            return is_owner or obj.assignee == request.user
        return is_owner or is_member


class IsCommentAuthor(BasePermission):
    """Allows deleting a comment only to its author."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
