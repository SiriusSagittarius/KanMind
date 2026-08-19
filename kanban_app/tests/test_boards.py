"""Tests for the board endpoints."""
from django.urls import reverse
from rest_framework import status

from kanban_app.models import Board

from .base import KanbanBaseTestCase


class BoardListCreateTests(KanbanBaseTestCase):
    """Tests listing and creating boards."""

    def setUp(self):
        super().setUp()
        self.url = reverse("board-list")

    def test_list_requires_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_sees_own_board(self):
        self.auth(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_member_sees_board(self):
        self.auth(self.member)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1)

    def test_outsider_sees_no_board(self):
        self.auth(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 0)

    def test_create_board(self):
        self.auth(self.owner)
        response = self.client.post(
            self.url, {"title": "New", "members": [self.member.id]}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Board.objects.count(), 2)

    def test_list_counts(self):
        self.make_task(status="to-do", priority="high")
        self.auth(self.owner)
        response = self.client.get(self.url)
        data = response.data[0]
        self.assertEqual(data["ticket_count"], 1)
        self.assertEqual(data["tasks_to_do_count"], 1)
        self.assertEqual(data["tasks_high_prio_count"], 1)
        self.assertEqual(data["member_count"], 1)


class BoardDetailTests(KanbanBaseTestCase):
    """Tests the detail view, updating and deleting a board."""

    def setUp(self):
        super().setUp()
        self.url = reverse("board-detail", args=[self.board.id])

    def test_detail_contains_members_and_tasks(self):
        self.make_task()
        self.auth(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["owner_id"], self.owner.id)
        self.assertEqual(len(response.data["members"]), 1)
        self.assertEqual(len(response.data["tasks"]), 1)

    def test_outsider_forbidden(self):
        self.auth(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_patch(self):
        self.auth(self.outsider)
        response = self.client.patch(self.url, {"title": "Hacked"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nonexistent_board_returns_404(self):
        self.auth(self.owner)
        url = reverse("board-detail", args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_can_patch(self):
        self.auth(self.member)
        response = self.client.patch(self.url, {"title": "Changed"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_cannot_delete(self):
        self.auth(self.member)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete(self):
        self.auth(self.owner)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Board.objects.count(), 0)
