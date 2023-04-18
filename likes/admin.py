from django.contrib import admin
from .models import Likes, LikeRecord
# Register your models here.


@admin.register(Likes)
class LikesAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'content_object', 'like_num')


@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_object', )