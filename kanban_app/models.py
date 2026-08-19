"""Data models of the kanban_app: board, task and comment."""
from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    """A kanban board with an owner and members."""

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_boards"
    )
    members = models.ManyToManyField(
        User, related_name="boards", blank=True
    )

    class Meta:
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ["id"]

    def __str__(self):
        return self.title


class Task(models.Model):
    """A task within a board."""

    STATUS_CHOICES = [
        ("to-do", "To-do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="to-do"
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="reviewing_tasks",
        null=True,
        blank=True,
    )
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["id"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """A comment on a task."""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"
