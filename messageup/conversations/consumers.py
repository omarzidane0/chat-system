from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Conversation, Message


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if self.user is None:
            await self.close(code=4401)
            return

        self.conversation_ids = await self.get_conversation_ids()
        self.groups = [f'conversation_{conversation_id}' for conversation_id in self.conversation_ids]
        for group in self.groups:
            await self.channel_layer.group_add(group, self.channel_name)

        await self.accept()
        await self.send_json({
            'type': 'sync',
            'messages': await self.get_messages(),
        })

    async def disconnect(self, close_code):
        for group in getattr(self, 'groups', []):
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get('type') != 'send':
            return

        try:
            conversation_id = int(content.get('conversation_id'))
        except (TypeError, ValueError):
            await self.send_json({'type': 'error', 'message': 'المحادثة غير صالحة.'})
            return

        text = content.get('content')
        if conversation_id not in self.conversation_ids:
            await self.send_json({'type': 'error', 'message': 'لا تملك صلاحية إرسال رسالة لهذه المحادثة.'})
            return
        if not isinstance(text, str) or not text.strip() or len(text) > 5000:
            await self.send_json({'type': 'error', 'message': 'يجب أن تكون الرسالة بين حرف واحد و5000 حرف.'})
            return

        message = await self.create_message(conversation_id, text.strip())
        await self.channel_layer.group_send(
            f'conversation_{conversation_id}',
            {'type': 'chat.message', 'message': message},
        )

    async def chat_message(self, event):
        await self.send_json({'type': 'message', 'message': event['message']})

    @database_sync_to_async
    def get_conversation_ids(self):
        return list(
            Conversation.objects.filter(participants=self.user).values_list('id', flat=True)
        )

    @database_sync_to_async
    def get_messages(self):
        messages = Message.objects.filter(
            conversation_id__in=self.conversation_ids,
        ).select_related('sender').order_by('created_at', 'id')
        return [self.serialize_message(message) for message in messages]

    @database_sync_to_async
    def create_message(self, conversation_id, text):
        message = Message.objects.create(
            conversation_id=conversation_id,
            sender=self.user,
            content=text,
        )
        return self.serialize_message(message)

    @staticmethod
    def serialize_message(message):
        return {
            'id': message.id,
            'conversation_id': message.conversation_id,
            'sender_id': message.sender_id,
            'sender': message.sender.username,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
        }