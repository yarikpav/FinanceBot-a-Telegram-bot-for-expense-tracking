from django.contrib import admin
from .models import UserQuery

@admin.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    list_display = ("user_id", "command", "message_text", "created_at")
    search_fields = ("user_id", "command", "message_text")
    list_filter = ("command", "created_at")
