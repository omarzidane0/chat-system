from django.conf import settings
from django.test import TestCase, TransactionTestCase, override_settings
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
import jwt

from accounts.models import Account
from .models import Conversation, Message
from messageup.asgi import application


class ConversationPageTests(TestCase):
	def test_page_lists_authenticated_users_conversations(self):
		current_user = Account.objects.create(username='current', email='current@example.com', password='hash')
		other_user = Account.objects.create(username='other', email='other@example.com', password='hash')
		conversation = Conversation.objects.create()
		conversation.participants.add(current_user, other_user)
		token = jwt.encode({'id': current_user.id}, settings.SECRET_KEY, algorithm='HS256')
		self.client.cookies['jwt_token'] = token

		response = self.client.get('/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'other')
		self.assertContains(response, f'data-conversation-id="{conversation.id}"')


@override_settings(ALLOWED_HOSTS=['testserver'])
class ConversationWebSocketTests(TransactionTestCase):
	async def test_message_is_saved_and_delivered_after_recipient_reconnects(self):
		sender, recipient, conversation = await sync_to_async(self.create_conversation)()
		sender_token = jwt.encode({'id': sender.id}, settings.SECRET_KEY, algorithm='HS256')
		recipient_token = jwt.encode({'id': recipient.id}, settings.SECRET_KEY, algorithm='HS256')

		sender_socket = WebsocketCommunicator(
			application,
			'/ws/conversations/',
			headers=[
				(b'cookie', f'jwt_token={sender_token}'.encode()),
				(b'origin', b'http://testserver'),
			],
		)
		connected, connection_details = await sender_socket.connect()
		self.assertTrue(connected, f'WebSocket connection was rejected: {connection_details}')
		self.assertEqual((await sender_socket.receive_json_from())['type'], 'sync')
		await sender_socket.send_json_to({
			'type': 'send',
			'conversation_id': conversation.id,
			'content': 'رسالة محفوظة',
		})
		sent_event = await sender_socket.receive_json_from()
		self.assertEqual(sent_event['type'], 'message')
		await sender_socket.disconnect()

		recipient_socket = WebsocketCommunicator(
			application,
			'/ws/conversations/',
			headers=[
				(b'cookie', f'jwt_token={recipient_token}'.encode()),
				(b'origin', b'http://testserver'),
			],
		)
		connected, _ = await recipient_socket.connect()
		self.assertTrue(connected)
		history = await recipient_socket.receive_json_from()
		self.assertEqual(history['type'], 'sync')
		self.assertEqual(history['messages'][0]['content'], 'رسالة محفوظة')
		await recipient_socket.disconnect()

		saved_content = await sync_to_async(
			lambda: Message.objects.get(conversation=conversation).content
		)()
		self.assertEqual(saved_content, 'رسالة محفوظة')

	@staticmethod
	def create_conversation():
		sender = Account.objects.create(username='sender', email='sender@example.com', password='hash')
		recipient = Account.objects.create(username='recipient', email='recipient@example.com', password='hash')
		conversation = Conversation.objects.create()
		conversation.participants.add(sender, recipient)
		return sender, recipient, conversation
