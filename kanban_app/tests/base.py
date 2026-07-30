"""Gemeinsame Test-Basis fuer die kanban_app."""
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from kanban_app.models import Board, Task


class KanbanBaseTestCase(APITestCase):
    """Stellt Nutzer, Tokens und ein Beispiel-Board bereit."""

    def setUp(self):
        self.owner = self._make_user("owner@test.de", "Owner Eins")
        self.member = self._make_user("member@test.de", "Member Zwei")
        self.outsider = self._make_user("out@test.de", "Otto Aussen")
        self.board = Board.objects.create(title="Testboard", owner=self.owner)
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
        """Setzt den Authorization-Header auf den Token des Nutzers."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {user.token}")

    def make_task(self, **kwargs):
        """Erstellt eine Task im Testboard mit sinnvollen Defaults."""
        defaults = {
            "board": self.board, "title": "Task", "status": "to-do",
            "priority": "medium",
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)
