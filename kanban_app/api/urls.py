"""URL-Routen der kanban_app (Boards, Tasks, Kommentare)."""
from django.urls import path

from .views import (
    AssignedTasksView,
    BoardDetailView,
    BoardListCreateView,
    CommentDeleteView,
    CommentListCreateView,
    ReviewingTasksView,
    TaskCreateView,
    TaskDetailView,
)

urlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name="board-list"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),

    path("tasks/assigned-to-me/", AssignedTasksView.as_view(), name="tasks-assigned"),
    path("tasks/reviewing/", ReviewingTasksView.as_view(), name="tasks-reviewing"),
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),

    path(
        "tasks/<int:task_id>/comments/",
        CommentListCreateView.as_view(),
        name="comment-list",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:pk>/",
        CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]
