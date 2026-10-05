# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Id(models.Model):
    user = models.OneToOneField("auth.user", on_delete=models.CASCADE, db_column='user_id', related_name='+')
    is_banned = models.BooleanField(default=False)
    unban_time = models.DateField(blank=True, null=True)
    ban_time = models.DateField(blank=True, null=True)
    ban_permanent = models.BooleanField(default=False)

    class Meta:
        db_table = 'id'
        verbose_name = "ID"
        verbose_name_plural = "ID"

    def __str__(self):
        return f"Id of {self.user.username}"

class Chicken_Impire_Player(models.Model):
    target_id = models.OneToOneField("main.Id", on_delete=models.CASCADE, related_name='+')
    permission = models.TextField(choices=[("player", "Игрок"), ("vip", "Vip-игрок"), ("admin", "Админ"), ("developer", "Разработчик")], default="player", null=False)

    class Meta():
        db_table = "ci_player"
        verbose_name = "Игрок куриной империи"
        verbose_name_plural = "Игроки куриной империи"

    def __str__(self):
        return f"Игрок куриной империи от ID {self.target_id.user.username}"


class CI_Farm(models.Model):
    player = models.ForeignKey("Chicken_Impire_Player", on_delete=models.CASCADE, related_name='+')
    money = models.IntegerField(null=False, default=0)
    chickens = models.JSONField(default=list, null=False)
    vmap = models.JSONField(default=dict, null=False)

    class Meta():
        db_table = "ci_farm"
        verbose_name = "Ферма в куриной империи"
        verbose_name_plural = "Фермы в куриной империи"

    def __str__(self):
        return f"Ферма в куриной империи игрока {self.player.target_id.user.username}"
