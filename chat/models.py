from django.db import models
from accounts.models import User # We need our custom User model

class Conversation(models.Model):
    # We use ManyToManyField so we can link two (or more) users to one chat
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Get the first two participants for a clean title
        users = self.participants.all()
        if users.count() == 2:
            return f"Chat between {users[0].username} and {users[1].username}"
        return f"Conversation {self.id}"

class Message(models.Model):
    # Link the message to a conversation
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    # Link to the user who sent the message
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    # The actual text of the message
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        # Sort messages by timestamp, newest last
        ordering = ['timestamp']