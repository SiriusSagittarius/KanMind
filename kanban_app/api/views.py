"""Views der kanban_app: Boards, Tasks und Comments."""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Board, Comment, Task
from .permissions import (
    IsBoardOwnerOrMember,
    IsCommentAuthor,
    IsTaskBoardMember,
)
from .serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskSerializer,
)


class BoardListCreateView(generics.ListCreateAPIView):
    """Listet die Boards des Nutzers und erstellt neue Boards."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BoardCreateSerializer
        return BoardListSerializer

    def create(self, request, *args, **kwargs):
        """Validates via BoardCreateSerializer, responds with BoardListSerializer fields."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=self.request.user)
        response_serializer = BoardListSerializer(board)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Ruft ein einzelnes Board ab, bearbeitet oder loescht es."""

    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return BoardUpdateSerializer
        return BoardDetailSerializer


class TaskCreateView(generics.CreateAPIView):
    """Erstellt eine neue Task."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Ensures the target board exists and the user is a member before creating."""
        board_id = request.data.get("board")
        board = get_object_or_404(Board, pk=board_id)
        user = request.user
        if board.owner != user and user not in board.members.all():
            return Response(
                {"detail": "You must be a member of the board to create a task."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Bearbeitet oder loescht eine einzelne Task."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember]


class AssignedTasksView(generics.ListAPIView):
    """Listet Tasks, die dem angemeldeten Nutzer zugewiesen sind."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTasksView(generics.ListAPIView):
    """Listet Tasks, die der angemeldete Nutzer reviewt."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class CommentListCreateView(generics.ListCreateAPIView):
    """Listet Kommentare einer Task und erstellt neue Kommentare."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def _get_task_or_404(self):
        return get_object_or_404(Task, pk=self.kwargs["task_id"])

    def _check_board_membership(self, task):
        user = self.request.user
        board = task.board
        if board.owner != user and user not in board.members.all():
            self.permission_denied(
                self.request,
                message="You must be a member of the task's board.",
            )

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        task = self._get_task_or_404()
        self._check_board_membership(task)

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"])

    def perform_create(self, serializer):
        task = self._get_task_or_404()
        serializer.save(author=self.request.user, task=task)


class CommentDeleteView(generics.DestroyAPIView):
    """Loescht einen Kommentar (nur der Autor)."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"])
