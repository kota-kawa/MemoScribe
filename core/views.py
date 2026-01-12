"""
Core views for MemoScribe.
Dashboard, settings, and search.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from notes.models import Note
from logs.models import DailyLog, DailyDigest
from documents.models import Document
from tasks.models import Task
from preferences.models import Preference, UserSettings
from audits.models import AuditLog
from core.llm import llm_provider


@login_required
def dashboard(request):
    """Main dashboard view."""
    today = timezone.now().date()

    # Get upcoming and today's tasks
    upcoming_tasks = Task.objects.filter(
        user=request.user,
        status__in=["todo", "doing"],
    ).filter(
        Q(due_at__date__lte=today) | Q(due_at__date__lte=today + timezone.timedelta(days=3))
    ).order_by("due_at", "-priority")[:5]

    # Recent notes
    recent_notes = Note.objects.filter(user=request.user).order_by("-created_at")[:5]

    # Recent logs
    recent_logs = DailyLog.objects.filter(user=request.user).order_by("-date")[:5]

    has_note = Note.objects.filter(user=request.user).exists()
    has_log = DailyLog.objects.filter(user=request.user).exists()
    has_document = Document.objects.filter(user=request.user).exists()
    onboarding_done = sum([has_log, has_note, has_document])
    onboarding_total = 3
    onboarding_percent = int(onboarding_done / onboarding_total * 100)

    # LLM usage stats
    llm_calls_today = AuditLog.objects.filter(
        user=request.user,
        event_type="llm_call",
        created_at__date=today,
    ).count()

    total_tokens_today = sum(
        log.payload.get("tokens", 0)
        for log in AuditLog.objects.filter(
            user=request.user,
            event_type="llm_call",
            created_at__date=today,
        )
    )

    # Generate daily suggestion if LLM is enabled
    daily_suggestion = None
    if llm_provider.is_available():
        # Simple suggestion based on tasks and recent activity
        if upcoming_tasks.exists():
            task_names = [t.title for t in upcoming_tasks[:3]]
            daily_suggestion = f"今日は以下のタスクに取り組みましょう: {', '.join(task_names)}"
        else:
            daily_suggestion = "今日のタスクはありません。新しいタスクを追加するか、メモを整理してみましょう。"
    else:
        if upcoming_tasks.exists():
            daily_suggestion = f"期限が近いタスクが{upcoming_tasks.count()}件あります。"
        else:
            daily_suggestion = "今日の予定を記録しましょう。"

    context = {
        "today": today,
        "upcoming_tasks": upcoming_tasks,
        "recent_notes": recent_notes,
        "recent_logs": recent_logs,
        "daily_suggestion": daily_suggestion,
        "llm_calls_today": llm_calls_today,
        "total_tokens_today": total_tokens_today,
        "llm_available": llm_provider.is_available(),
        "show_onboarding": onboarding_done < onboarding_total,
        "onboarding_done": onboarding_done,
        "onboarding_total": onboarding_total,
        "onboarding_percent": onboarding_percent,
        "has_log": has_log,
        "has_note": has_note,
        "has_document": has_document,
    }
    return render(request, "dashboard.html", context)


@login_required
def settings_view(request):
    """User settings view."""
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Update settings
        user_settings.send_notes = request.POST.get("send_notes") == "on"
        user_settings.send_digests = request.POST.get("send_digests") == "on"
        user_settings.send_docs = request.POST.get("send_docs") == "on"
        user_settings.send_raw_logs = request.POST.get("send_raw_logs") == "on"
        user_settings.pii_masking = request.POST.get("pii_masking") == "on"
        user_settings.llm_enabled = request.POST.get("llm_enabled") == "on"
        user_settings.save()

        messages.success(request, "設定を保存しました。")
        return redirect("settings")

    context = {
        "settings": user_settings,
        "llm_configured": bool(llm_provider.api_key),
    }
    return render(request, "settings.html", context)


@login_required
def search_view(request):
    """Global search view."""
    query = request.GET.get("q", "").strip()
    results = {
        "notes": [],
        "digests": [],
        "documents": [],
        "tasks": [],
        "preferences": [],
    }

    if query:
        # Search notes
        results["notes"] = Note.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )[:10]

        # Search digests
        results["digests"] = DailyDigest.objects.filter(
            user=request.user
        ).filter(
            Q(summary__icontains=query) | Q(topics__icontains=query)
        )[:10]

        # Search documents
        results["documents"] = Document.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) | Q(extracted_text__icontains=query)
        )[:10]

        # Search tasks
        results["tasks"] = Task.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:10]

        # Search preferences
        results["preferences"] = Preference.objects.filter(
            user=request.user
        ).filter(
            Q(key__icontains=query) | Q(value__icontains=query)
        )[:10]

    total_results = sum(len(v) for v in results.values())

    context = {
        "query": query,
        "results": results,
        "total_results": total_results,
    }
    return render(request, "search.html", context)
