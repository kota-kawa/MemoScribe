"""
Tasks views for MemoScribe.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from tasks.models import Task
from tasks.forms import TaskForm


@login_required
def task_list(request):
    """List all tasks for the current user."""
    tasks = Task.objects.filter(user=request.user)

    # Filter by status
    status = request.GET.get("status")
    if status and status in ["todo", "doing", "done"]:
        tasks = tasks.filter(status=status)

    # Filter by tag
    tag = request.GET.get("tag")
    if tag:
        tasks = tasks.filter(tags__contains=[tag])

    context = {
        "tasks": tasks,
        "selected_status": status,
        "selected_tag": tag,
    }
    return render(request, "tasks/list.html", context)


@login_required
def task_detail(request, pk):
    """Display a single task."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    context = {"task": task}
    return render(request, "tasks/detail.html", context)


@login_required
def task_create(request):
    """Create a new task."""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user

            # Parse tags
            tags_str = request.POST.get("tags_input", "")
            task.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            task.save()
            messages.success(request, "タスクを作成しました。")
            return redirect("tasks:detail", pk=task.pk)
    else:
        form = TaskForm()

    context = {"form": form, "is_edit": False}
    return render(request, "tasks/form.html", context)


@login_required
def task_edit(request, pk):
    """Edit an existing task."""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)

            # Parse tags
            tags_str = request.POST.get("tags_input", "")
            task.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            task.save()
            messages.success(request, "タスクを更新しました。")
            return redirect("tasks:detail", pk=task.pk)
    else:
        form = TaskForm(instance=task)

    context = {"form": form, "task": task, "is_edit": True}
    return render(request, "tasks/form.html", context)


@login_required
def task_delete(request, pk):
    """Delete a task."""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == "POST":
        task.delete()
        messages.success(request, "タスクを削除しました。")
        return redirect("tasks:list")

    context = {"task": task}
    return render(request, "tasks/delete.html", context)


@login_required
def task_toggle_status(request, pk):
    """Quick toggle task status."""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["todo", "doing", "done"]:
            task.status = new_status
            task.save()
            messages.success(request, f"タスクを「{task.get_status_display()}」に変更しました。")

    return redirect(request.META.get("HTTP_REFERER", "tasks:list"))
