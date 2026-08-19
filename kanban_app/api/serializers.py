"""Serializer der kanban_app: Board, Task und Comment."""
from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import Board, Comment, Task


class UserShortSerializer(serializers.ModelSerializer):
    """Kompakte Nutzerdarstellung (id, email, fullname) fuer Einbettungen."""

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        return obj.get_full_name()


class BoardListSerializer(serializers.ModelSerializer):
    """Board-Darstellung fuer die Listenansicht inkl. Zaehlern."""

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.PrimaryKeyRelatedField(source="owner", read_only=True)

    class Meta:
        model = Board
        fields = [
            "id", "title", "member_count", "ticket_count",
            "tasks_to_do_count", "tasks_high_prio_count", "owner_id",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()


class BoardCreateSerializer(serializers.ModelSerializer):
    """Serializer zum Anlegen eines Boards (Titel + Mitglieder-IDs)."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )

    class Meta:
        model = Board
        fields = ["id", "title", "members"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Board update: accepts title/members, responds with owner_data/members_data."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False, write_only=True
    )
    owner_data = UserShortSerializer(source="owner", read_only=True)
    members_data = UserShortSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members", "members_data"]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Board-Detailansicht inkl. Mitgliederliste und Tasks."""

    members = UserShortSerializer(many=True, read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(source="owner", read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_tasks(self, obj):
        return TaskSerializer(obj.tasks.all(), many=True).data


class TaskSerializer(serializers.ModelSerializer):
    """Task-Serializer: liest Objekte, schreibt per *_id-Feldern."""

    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="assignee",
        write_only=True, required=False, allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="reviewer",
        write_only=True, required=False, allow_null=True,
    )
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description", "status", "priority",
            "assignee", "reviewer", "assignee_id", "reviewer_id",
            "due_date", "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    """Kommentar-Serializer; author wird als voller Name ausgegeben."""

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]

    def get_author(self, obj):
        return obj.author.get_full_name()
