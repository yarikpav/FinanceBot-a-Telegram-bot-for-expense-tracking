from django.db import models

class UserQuery(models.Model):
    user_id = models.BigIntegerField()
    command = models.CharField(max_length=50)
    message_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} | {self.command} | {self.created_at}"
