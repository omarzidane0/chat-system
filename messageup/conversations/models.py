from django.db import models

# Create your models here.
class Conversation(models.Model):
    participants = models.ManyToManyField('accounts.Account', related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    is_group = models.BooleanField(default=False)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey('accounts.Account', related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']