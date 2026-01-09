"""
Logs views for MemoScribe.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from logs.models import DailyLog, DailyDigest
from logs.forms import DailyLogForm


@login_required
def log_list(request):
    """List all daily logs for the current user."""
    logs = DailyLog.objects.filter(user=request.user).select_related("digest")
    context = {"logs": logs}
    return render(request, "logs/list.html", context)


@login_required
def log_detail(request, pk):
    """Display a single daily log with its digest."""
    log = get_object_or_404(DailyLog, pk=pk, user=request.user)

    # Get digest if exists
    digest = getattr(log, "digest", None)

    context = {"log": log, "digest": digest}
    return render(request, "logs/detail.html", context)


@login_required
def log_create(request):
    """Create a new daily log."""
    today = timezone.now().date()

    # Check if log exists for today
    existing_log = DailyLog.objects.filter(user=request.user, date=today).first()
    if existing_log:
        messages.info(request, "今日のログは既に存在します。編集画面に移動します。")
        return redirect("logs:edit", pk=existing_log.pk)

    if request.method == "POST":
        form = DailyLogForm(request.POST, request.FILES)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            messages.success(request, "ログを作成しました。ダイジェストを生成中...")
            return redirect("logs:detail", pk=log.pk)
    else:
        form = DailyLogForm(initial={"date": today})

    context = {"form": form, "is_edit": False}
    return render(request, "logs/form.html", context)


@login_required
def log_edit(request, pk):
    """Edit an existing daily log."""
    log = get_object_or_404(DailyLog, pk=pk, user=request.user)

    if request.method == "POST":
        form = DailyLogForm(request.POST, request.FILES, instance=log)
        if form.is_valid():
            log = form.save()
            messages.success(request, "ログを更新しました。ダイジェストを再生成中...")
            return redirect("logs:detail", pk=log.pk)
    else:
        form = DailyLogForm(instance=log)

    context = {"form": form, "log": log, "is_edit": True}
    return render(request, "logs/form.html", context)


@login_required
def log_delete(request, pk):
    """Delete a daily log."""
    log = get_object_or_404(DailyLog, pk=pk, user=request.user)

    if request.method == "POST":
        log.delete()
        messages.success(request, "ログを削除しました。")
        return redirect("logs:list")

    context = {"log": log}
    return render(request, "logs/delete.html", context)


@login_required
def log_digest(request, pk):
    """View digest for a specific log."""
    log = get_object_or_404(DailyLog, pk=pk, user=request.user)
    digest = getattr(log, "digest", None)

    if not digest:
        messages.warning(request, "ダイジェストはまだ生成されていません。")
        return redirect("logs:detail", pk=log.pk)

    context = {"log": log, "digest": digest}
    return render(request, "logs/digest.html", context)
