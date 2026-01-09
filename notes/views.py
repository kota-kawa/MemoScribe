"""
Notes views for MemoScribe.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import markdown
import bleach

from notes.models import Note
from notes.forms import NoteForm


@login_required
def note_list(request):
    """List all notes for the current user."""
    notes = Note.objects.filter(user=request.user)

    # Filter by tag if specified
    tag = request.GET.get("tag")
    if tag:
        notes = notes.filter(tags__contains=[tag])

    context = {"notes": notes, "selected_tag": tag}
    return render(request, "notes/list.html", context)


@login_required
def note_detail(request, pk):
    """Display a single note."""
    note = get_object_or_404(Note, pk=pk, user=request.user)

    # Render markdown safely
    html_body = markdown.markdown(note.body, extensions=["fenced_code", "tables"])
    html_body = bleach.clean(
        html_body,
        tags=["p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "a", "code", "pre", "em", "strong", "table", "thead", "tbody", "tr", "th", "td", "br", "blockquote"],
        attributes={"a": ["href", "title"]},
    )

    context = {"note": note, "html_body": html_body}
    return render(request, "notes/detail.html", context)


@login_required
def note_create(request):
    """Create a new note."""
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user

            # Parse tags from comma-separated string
            tags_str = request.POST.get("tags_input", "")
            note.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            note.save()
            messages.success(request, "メモを作成しました。")
            return redirect("notes:detail", pk=note.pk)
    else:
        form = NoteForm()

    context = {"form": form, "is_edit": False}
    return render(request, "notes/form.html", context)


@login_required
def note_edit(request, pk):
    """Edit an existing note."""
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save(commit=False)

            # Parse tags
            tags_str = request.POST.get("tags_input", "")
            note.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            note.save()
            messages.success(request, "メモを更新しました。")
            return redirect("notes:detail", pk=note.pk)
    else:
        form = NoteForm(instance=note)

    context = {"form": form, "note": note, "is_edit": True}
    return render(request, "notes/form.html", context)


@login_required
def note_delete(request, pk):
    """Delete a note."""
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == "POST":
        note.delete()
        messages.success(request, "メモを削除しました。")
        return redirect("notes:list")

    context = {"note": note}
    return render(request, "notes/delete.html", context)
