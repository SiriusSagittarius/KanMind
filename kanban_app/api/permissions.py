"""Zugriffskontrolle der kanban_app."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsBoardOwnerOrMember(BasePermission):
    """Erlaubt Zugriff nur dem Board-Besitzer oder dessen Mitgliedern.

    Das Loeschen eines Boards ist ausschliesslich dem Besitzer erlaubt.
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        is_member = request.user in obj.members.all()
        if request.method == "DELETE":
            return is_owner
        return is_owner or is_member


class IsTaskBoardMember(BasePermission):
    """Erlaubt Task-Zugriff nur Mitgliedern (oder Besitzer) des Boards.

    Das Loeschen einer Task ist dem Ersteller (assignee) oder dem
    Board-Besitzer vorbehalten.
    """

    def has_object_permission(self, request, view, obj):
        board = obj.board
        is_owner = board.owner == request.user
        is_member = request.user in board.members.all()
        if request.method == "DELETE":
            return is_owner or obj.assignee == request.user
        return is_owner or is_member


class IsCommentAuthor(BasePermission):
    """Erlaubt Aenderungen an einem Kommentar nur dessen Autor."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
