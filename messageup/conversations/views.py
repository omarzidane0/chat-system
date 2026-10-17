import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from accounts.decorators import jwt_required
from accounts.models import Account
from .models import Conversation


@jwt_required
def conversations_view(request):
    user = request.jwt_user
    conversations = []
    for conversation in user.conversations.prefetch_related('participants').order_by('-created_at'):
        participants = list(conversation.participants.exclude(id=user.id))
        if conversation.is_group:
            name = ', '.join(participant.username for participant in participants) or 'محادثة جماعية'
        else:
            name = participants[0].username if participants else 'محادثة جديدة'
        initials = ''.join(participant.username[:1] for participant in participants[:2]) or '?'
        last_message = conversation.messages.select_related('sender').order_by('-created_at').first()
        conversations.append({
            'id': conversation.id,
            'name': name,
            'initials': initials,
            'is_group': conversation.is_group,
            'last_message': last_message,
        })

    contacts = Account.objects.exclude(id=user.id).order_by('username')
    return render(request, 'conversations.html', {
        'current_user': user,
        'conversations': conversations,
        'contacts': contacts,
    })


@require_POST
@jwt_required
def create_conversation(request):
    try:
        data = json.loads(request.body)
        participant_ids = {int(value) for value in data.get('participant_ids', [])}
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'قائمة المشاركين غير صالحة.'}, status=400)

    participant_ids.discard(request.jwt_user.id)
    if not participant_ids:
        return JsonResponse({'error': 'اختر مشاركاً واحداً على الأقل.'}, status=400)

    participants = list(Account.objects.filter(id__in=participant_ids))
    if len(participants) != len(participant_ids):
        return JsonResponse({'error': 'أحد المشاركين غير موجود.'}, status=400)

    conversation = Conversation.objects.create(is_group=len(participants) > 1)
    conversation.participants.add(request.jwt_user, *participants)
    return JsonResponse({'id': conversation.id}, status=201)