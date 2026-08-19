"""Tests for the comment endpoints."""
from django.urls import reverse
from rest_framework import status

from kanban_app.models import Comment

from .base import KanbanBaseTestCase


class CommentTests(KanbanBaseTestCase):
    """Tests listing, creating and deleting comments."""

    def setUp(self):
        super().setUp()
        self.task = self.make_task(assignee=self.member)
        self.list_url = reverse("comment-list", args=[self.task.id])

    def test_create_comment(self):
        self.auth(self.member)
        response = self.client.post(self.list_url, {"content": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], "Member Two")
        self.assertEqual(response.data["content"], "Hello")

    def test_list_comments(self):
        Comment.objects.create(
            task=self.task, author=self.owner, content="First"
        )
        self.auth(self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_requires_auth(self):
        response = self.client.post(self.list_url, {"content": "X"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_outsider_cannot_list_comments(self):
        self.auth(self.outsider)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_create_comment(self):
        self.auth(self.outsider)
        response = self.client.post(self.list_url, {"content": "X"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comments_for_unknown_task_return_404(self):
        self.auth(self.owner)
        url = reverse("comment-list", args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_author_can_delete(self):
        comment = Comment.objects.create(
            task=self.task, author=self.member, content="Mine"
        )
        self.auth(self.member)
        url = reverse("comment-delete", args=[self.task.id, comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_non_author_cannot_delete(self):
        comment = Comment.objects.create(
            task=self.task, author=self.member, content="Mine"
        )
        self.auth(self.owner)
        url = reverse("comment-delete", args=[self.task.id, comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_unknown_comment_returns_404(self):
        self.auth(self.owner)
        url = reverse("comment-delete", args=[self.task.id, 999999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ModelStrTests(KanbanBaseTestCase):
    """Tests the __str__ methods of the models."""

    def test_str_methods(self):
        task = self.make_task(title="My Task")
        comment = Comment.objects.create(
            task=task, author=self.owner, content="Text"
        )
        self.assertEqual(str(self.board), "Test Board")
        self.assertEqual(str(task), "My Task")
        self.assertIn("owner@test.de", str(comment))
