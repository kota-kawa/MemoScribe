"""
Tasks forms for MemoScribe.
"""

from django import forms
from tasks.models import Task


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks."""

    class Meta:
        model = Task
        fields = ["title", "description", "due_at", "priority", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "タスク名"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "詳細説明"}),
            "due_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
