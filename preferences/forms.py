"""
Preferences forms for MemoScribe.
"""

from django import forms
from preferences.models import Preference


class PreferenceForm(forms.ModelForm):
    """Form for creating and editing preferences."""

    class Meta:
        model = Preference
        fields = ["key", "value", "category"]
        widgets = {
            "key": forms.TextInput(attrs={"class": "form-control", "placeholder": "例: 文章スタイル"}),
            "value": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "例: 丁寧でフォーマルな文体を好む"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }
