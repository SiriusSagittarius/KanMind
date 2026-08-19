"""Shared test base for the kanban_app."""
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from kanban_app.models import Board, Task


class KanbanBaseTestCase(APITestCase):
    """Provides users, tokens and a sample board."""

    def setUp(self):
        self.owner = self._make_user("owner@test.de", "Owner One")
        self.member = self._make_user("member@test.de", "Member Two")
        self.outsider = self._make_user("out@test.de", "Otto Outsider")
        self.board = Board.objects.create(title="Test Board", owner=self.owner)
        self.board.members.add(self.member)

    def _make_user(self, email, fullname):
        first, last = fullname.split(" ", 1)
        user = User.objects.create_user(
            username=email, email=email, password="geheim123",
            first_name=first, last_name=last,
        )
        user.token = Token.objects.create(user=user).key
        return user

    def auth(self, user):
        """Sets the Authorization header to the user's token."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {user.token}")

    def make_task(self, **kwargs):
        """Creates a task on the test board with sensible defaults."""
        defaults = {
            "board": self.board, "title": "Task", "status": "to-do",
            "priority": "medium",
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)
