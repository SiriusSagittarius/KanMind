"""Tests der Kommentar-Endpunkte."""
from django.urls import reverse
from rest_framework import status

from kanban_app.models import Comment

from .base import KanbanBaseTestCase


class CommentTests(KanbanBaseTestCase):
    """Testet Auflistung, Erstellung und Loeschen von Kommentaren."""

    def setUp(self):
        super().setUp()
        self.task = self.make_task(assignee=self.member)
        self.list_url = reverse("comment-list", args=[self.task.id])

    def test_create_comment(self):
        self.auth(self.member)
        response = self.client.post(self.list_url, {"content": "Hallo"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], "Member Zwei")
        self.assertEqual(response.data["content"], "Hallo")

    def test_list_comments(self):
        Comment.objects.create(
            task=self.task, author=self.owner, content="Erster"
        )
        self.auth(self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_requires_auth(self):
        response = self.client.post(self.list_url, {"content": "X"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_author_can_delete(self):
        comment = Comment.objects.create(
            task=self.task, author=self.member, content="Meins"
        )
        self.auth(self.member)
        url = reverse("comment-delete", args=[self.task.id, comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_non_author_cannot_delete(self):
        comment = Comment.objects.create(
            task=self.task, author=self.member, content="Meins"
        )
        self.auth(self.owner)
        url = reverse("comment-delete", args=[self.task.id, comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ModelStrTests(KanbanBaseTestCase):
    """Testet die __str__-Methoden der Modelle."""

    def test_str_methods(self):
        task = self.make_task(title="Meine Task")
        comment = Comment.objects.create(
            task=task, author=self.owner, content="Text"
        )
        self.assertEqual(str(self.board), "Testboard")
        self.assertEqual(str(task), "Meine Task")
        self.assertIn("owner@test.de", str(comment))
