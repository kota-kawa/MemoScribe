"""
Assistant views for MemoScribe chat.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from assistant.models import ChatSession, ChatMessage
from retrieval.services import RetrievalService
from core.llm import llm_provider
from core.utils import calculate_token_estimate
from audits.models import AuditLog


@login_required
def session_list(request):
    """List all chat sessions for the current user."""
    sessions = ChatSession.objects.filter(user=request.user)
    context = {"sessions": sessions}
    return render(request, "assistant/list.html", context)


@login_required
def session_create(request):
    """Create a new chat session."""
    session = ChatSession.objects.create(user=request.user)
    return redirect("assistant:session", pk=session.pk)


@login_required
def session_detail(request, pk):
    """Display a chat session with messages."""
    session = get_object_or_404(ChatSession, pk=pk, user=request.user)
    messages_list = session.messages.all()

    # Get writing templates
    writing_templates = [
        {"id": "email_polite", "name": "丁寧なメール"},
        {"id": "email_casual", "name": "カジュアルなメール"},
        {"id": "rewrite_short", "name": "短くリライト"},
        {"id": "rewrite_polite", "name": "丁寧にリライト"},
        {"id": "rewrite_logical", "name": "論理的にリライト"},
        {"id": "daily_plan", "name": "今日の予定提案"},
    ]

    context = {
        "session": session,
        "messages": messages_list,
        "writing_templates": writing_templates,
        "llm_available": llm_provider.is_available(),
    }
    return render(request, "assistant/session.html", context)


@login_required
@require_POST
def send_message(request, pk):
    """Send a message and get assistant response."""
    session = get_object_or_404(ChatSession, pk=pk, user=request.user)
    user_message = request.POST.get("message", "").strip()

    if not user_message:
        messages.error(request, "メッセージを入力してください。")
        return redirect("assistant:session", pk=pk)

    # Save user message
    ChatMessage.objects.create(
        session=session,
        role="user",
        content=user_message,
    )

    # Update session title if first message
    if session.messages.count() == 1:
        session.title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        session.save()

    # Retrieve relevant context
    retrieval_service = RetrievalService(request.user)
    context_items = retrieval_service.retrieve(user_message)
    preferences = retrieval_service.get_user_preferences()

    # Generate response
    response = llm_provider.generate_assistant_response(
        question=user_message,
        context_items=context_items,
        preferences=preferences,
    )

    # Save assistant message
    ChatMessage.objects.create(
        session=session,
        role="assistant",
        content=response.get("answer", "申し訳ありません。回答を生成できませんでした。"),
        citations=response.get("citations", []),
        next_questions=response.get("next_questions", []),
    )

    # Log LLM call
    if llm_provider.is_available():
        AuditLog.objects.create(
            user=request.user,
            event_type="llm_call",
            payload={
                "action": "assistant_response",
                "session_id": session.pk,
                "tokens": calculate_token_estimate(user_message + str(context_items)),
                "context_count": len(context_items),
            },
        )

    return redirect("assistant:session", pk=pk)


@login_required
@require_POST
def generate_writing(request, pk):
    """Generate writing based on template."""
    session = get_object_or_404(ChatSession, pk=pk, user=request.user)
    template_type = request.POST.get("template", "")
    user_input = request.POST.get("input", "").strip()

    if not user_input:
        messages.error(request, "入力を指定してください。")
        return redirect("assistant:session", pk=pk)

    # Save user message
    template_names = {
        "email_polite": "丁寧なメール作成",
        "email_casual": "カジュアルなメール作成",
        "rewrite_short": "短くリライト",
        "rewrite_polite": "丁寧にリライト",
        "rewrite_logical": "論理的にリライト",
        "daily_plan": "今日の予定提案",
    }
    template_name = template_names.get(template_type, "文章生成")

    ChatMessage.objects.create(
        session=session,
        role="user",
        content=f"【{template_name}】\n{user_input}",
    )

    # Retrieve relevant context
    retrieval_service = RetrievalService(request.user)
    context_items = retrieval_service.retrieve(user_input)
    preferences = retrieval_service.get_user_preferences()

    # Generate writing
    response = llm_provider.generate_writing(
        template_type=template_type,
        user_input=user_input,
        context_items=context_items,
        preferences=preferences,
    )

    # Format response with citations
    output = response.get("output", "文章を生成できませんでした。")
    citations = response.get("citations", [])
    missing_info = response.get("missing_info", [])

    if missing_info:
        output += f"\n\n【不足情報】\n" + "\n".join(f"- {info}" for info in missing_info)

    # Save assistant message
    ChatMessage.objects.create(
        session=session,
        role="assistant",
        content=output,
        citations=citations,
    )

    # Log LLM call
    if llm_provider.is_available():
        AuditLog.objects.create(
            user=request.user,
            event_type="llm_call",
            payload={
                "action": "generate_writing",
                "template": template_type,
                "session_id": session.pk,
                "tokens": calculate_token_estimate(user_input + str(context_items)),
            },
        )

    return redirect("assistant:session", pk=pk)


@login_required
def session_delete(request, pk):
    """Delete a chat session."""
    session = get_object_or_404(ChatSession, pk=pk, user=request.user)

    if request.method == "POST":
        session.delete()
        messages.success(request, "チャットセッションを削除しました。")
        return redirect("assistant:list")

    context = {"session": session}
    return render(request, "assistant/delete.html", context)
