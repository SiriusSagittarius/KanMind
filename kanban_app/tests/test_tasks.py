"""Tests der Task-Endpunkte."""
from django.urls import reverse
from rest_framework import status

from kanban_app.models import Task

from .base import KanbanBaseTestCase


class TaskCreateTests(KanbanBaseTestCase):
    """Testet die Erstellung von Tasks."""

    def setUp(self):
        super().setUp()
        self.url = reverse("task-create")
        self.payload = {
            "board": self.board.id, "title": "Neue Task",
            "description": "Text", "status": "to-do", "priority": "high",
            "assignee_id": self.member.id, "reviewer_id": self.owner.id,
            "due_date": "2026-08-15",
        }

    def test_create_task(self):
        self.auth(self.owner)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["assignee"]["id"], self.member.id)
        self.assertEqual(response.data["reviewer"]["id"], self.owner.id)
        self.assertEqual(response.data["comments_count"], 0)

    def test_create_requires_auth(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskDetailTests(KanbanBaseTestCase):
    """Testet Bearbeiten und Loeschen einzelner Tasks."""

    def setUp(self):
        super().setUp()
        self.task = self.make_task(assignee=self.member)
        self.url = reverse("task-detail", args=[self.task.id])

    def test_member_can_patch_status(self):
        self.auth(self.member)
        response = self.client.patch(self.url, {"status": "in-progress"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "in-progress")

    def test_outsider_forbidden(self):
        self.auth(self.outsider)
        response = self.client.patch(self.url, {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete(self):
        self.auth(self.owner)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_assignee_can_delete(self):
        self.auth(self.member)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TaskFilterTests(KanbanBaseTestCase):
    """Testet die Filter-Endpunkte assigned-to-me und reviewing."""

    def setUp(self):
        super().setUp()
        self.make_task(assignee=self.member, reviewer=self.owner)

    def test_assigned_to_me(self):
        self.auth(self.member)
        response = self.client.get(reverse("tasks-assigned"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_reviewing(self):
        self.auth(self.owner)
        response = self.client.get(reverse("tasks-reviewing"))
        self.assertEqual(len(response.data), 1)

    def test_assigned_empty_for_others(self):
        self.auth(self.outsider)
        response = self.client.get(reverse("tasks-assigned"))
        self.assertEqual(len(response.data), 0)
