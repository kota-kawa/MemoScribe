"""
Documents forms for MemoScribe.
"""

from django import forms
from documents.models import Document


class DocumentForm(forms.ModelForm):
    """Form for uploading documents."""

    class Meta:
        model = Document
        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "文書タイトル"}),
            "file": forms.FileInput(attrs={"class": "form-control", "accept": ".pdf,.txt,.md"}),
        }
