"""Tests for models."""

import pytest
from django.contrib.auth.models import User


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.mark.django_db
class TestNoteModel:
    """Tests for Note model."""

    def test_create_note(self, user):
        from notes.models import Note

        note = Note.objects.create(
            user=user,
            title="Test Note",
            body="This is a test note.",
            tags=["test", "sample"],
            importance=3,
        )
        assert note.pk is not None
        assert note.title == "Test Note"
        assert "test" in note.tags
        assert note.get_tags_display() == "test, sample"

    def test_note_str(self, user):
        from notes.models import Note

        note = Note.objects.create(user=user, title="My Note", body="Content")
        assert str(note) == "My Note"


@pytest.mark.django_db
class TestDailyLogModel:
    """Tests for DailyLog model."""

    def test_create_log(self, user):
        from logs.models import DailyLog
        from django.utils import timezone

        log = DailyLog.objects.create(
            user=user,
            date=timezone.now().date(),
            raw_text="今日は良い日だった。",
            mood=4,
        )
        assert log.pk is not None
        assert log.raw_text == "今日は良い日だった。"


@pytest.mark.django_db
class TestTaskModel:
    """Tests for Task model."""

    def test_create_task(self, user):
        from tasks.models import Task

        task = Task.objects.create(
            user=user,
            title="Important Task",
            description="Do something important",
            priority=3,
            status="todo",
        )
        assert task.pk is not None
        assert task.status == "todo"
        assert task.is_overdue is False

    def test_task_overdue(self, user):
        from tasks.models import Task
        from django.utils import timezone
        import datetime

        task = Task.objects.create(
            user=user,
            title="Overdue Task",
            due_at=timezone.now() - datetime.timedelta(days=1),
            status="todo",
        )
        assert task.is_overdue is True


@pytest.mark.django_db
class TestPreferenceModel:
    """Tests for Preference model."""

    def test_create_preference(self, user):
        from preferences.models import Preference

        pref = Preference.objects.create(
            user=user,
            key="文章スタイル",
            value="丁寧な敬語を使う",
            category="writing",
        )
        assert pref.pk is not None
        assert "文章スタイル" in str(pref)
