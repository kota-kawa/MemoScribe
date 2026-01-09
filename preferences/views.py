"""
Preferences views for MemoScribe.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from preferences.models import Preference
from preferences.forms import PreferenceForm


@login_required
def preference_list(request):
    """List all preferences for the current user."""
    preferences = Preference.objects.filter(user=request.user)

    # Group by category
    grouped = {}
    for pref in preferences:
        cat = pref.get_category_display()
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(pref)

    context = {"preferences": preferences, "grouped": grouped}
    return render(request, "preferences/list.html", context)


@login_required
def preference_create(request):
    """Create a new preference."""
    if request.method == "POST":
        form = PreferenceForm(request.POST)
        if form.is_valid():
            preference = form.save(commit=False)
            preference.user = request.user

            # Check for duplicate key
            if Preference.objects.filter(user=request.user, key=preference.key).exists():
                messages.error(request, "同じキーの設定が既に存在します。")
                return render(request, "preferences/form.html", {"form": form, "is_edit": False})

            preference.save()
            messages.success(request, "設定を作成しました。")
            return redirect("preferences:list")
    else:
        form = PreferenceForm()

    context = {"form": form, "is_edit": False}
    return render(request, "preferences/form.html", context)


@login_required
def preference_edit(request, pk):
    """Edit an existing preference."""
    preference = get_object_or_404(Preference, pk=pk, user=request.user)

    if request.method == "POST":
        form = PreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, "設定を更新しました。")
            return redirect("preferences:list")
    else:
        form = PreferenceForm(instance=preference)

    context = {"form": form, "preference": preference, "is_edit": True}
    return render(request, "preferences/form.html", context)


@login_required
def preference_delete(request, pk):
    """Delete a preference."""
    preference = get_object_or_404(Preference, pk=pk, user=request.user)

    if request.method == "POST":
        preference.delete()
        messages.success(request, "設定を削除しました。")
        return redirect("preferences:list")

    context = {"preference": preference}
    return render(request, "preferences/delete.html", context)
