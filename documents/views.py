"""
Documents views for MemoScribe.
"""

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from documents.models import Document
from documents.forms import DocumentForm


@login_required
def document_list(request):
    """List all documents for the current user."""
    documents = Document.objects.filter(user=request.user)
    context = {"documents": documents}
    return render(request, "documents/list.html", context)


@login_required
def document_detail(request, pk):
    """Display a single document with its extracted text."""
    document = get_object_or_404(Document, pk=pk, user=request.user)
    chunks = document.chunks.all()

    context = {"document": document, "chunks": chunks}
    return render(request, "documents/detail.html", context)


@login_required
def document_create(request):
    """Upload a new document."""
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user

            # Determine file type from extension
            file_name = document.file.name.lower()
            if file_name.endswith(".pdf"):
                document.file_type = "pdf"
            elif file_name.endswith(".md"):
                document.file_type = "md"
            else:
                document.file_type = "txt"

            document.save()
            messages.success(request, "文書をアップロードしました。処理中...")
            return redirect("documents:detail", pk=document.pk)
    else:
        form = DocumentForm()

    context = {"form": form}
    return render(request, "documents/form.html", context)


@login_required
def document_delete(request, pk):
    """Delete a document."""
    document = get_object_or_404(Document, pk=pk, user=request.user)

    if request.method == "POST":
        # Delete the file
        if document.file:
            try:
                os.remove(document.file.path)
            except OSError:
                pass
        document.delete()
        messages.success(request, "文書を削除しました。")
        return redirect("documents:list")

    context = {"document": document}
    return render(request, "documents/delete.html", context)
