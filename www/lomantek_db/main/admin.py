from django.contrib import admin, messages
from django.utils import timezone
from datetime import timedelta
from main import models

@admin.action(description="Забанить")
def ban(modeladmin, request, queryset):
    # Обновляем выбранные записи в базе данных
    updated = queryset.update(is_banned=True, ban_time=timezone.now().date(), unban_time=timezone.now().date() + timedelta(days=30), ban_permanent=False)


    modeladmin.message_user(
    request,
    "Успешно забанены выбранные пользователи! Срок бана: 30 дней, можно изменить в админке!",
    messages.SUCCESS
    )
# Register your models here
@admin.register(models.Id)
class ID_ADMIN(admin.ModelAdmin):
    actions = [ban]

admin.site.register(models.Chicken_Impire_Player)
admin.site.register(models.CI_Farm)
