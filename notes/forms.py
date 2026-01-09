"""
Notes forms for MemoScribe.
"""

from django import forms
from notes.models import Note


class NoteForm(forms.ModelForm):
    """Form for creating and editing notes."""

    class Meta:
        model = Note
        fields = ["title", "body", "importance", "visibility"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "タイトル"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 10, "placeholder": "本文（Markdown対応）"}),
            "importance": forms.Select(attrs={"class": "form-select"}),
            "visibility": forms.Select(attrs={"class": "form-select"}),
        }
