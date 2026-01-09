"""
Logs forms for MemoScribe.
"""

from django import forms
from logs.models import DailyLog


class DailyLogForm(forms.ModelForm):
    """Form for creating and editing daily logs."""

    class Meta:
        model = DailyLog
        fields = ["date", "raw_text", "mood", "attachment"]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "raw_text": forms.Textarea(attrs={"class": "form-control", "rows": 8, "placeholder": "今日の出来事を記録..."}),
            "mood": forms.Select(attrs={"class": "form-select"}),
            "attachment": forms.FileInput(attrs={"class": "form-control"}),
        }
