from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from .models import Likes, LikeRecord
from django.http import JsonResponse
# Create your views here.


def errorsponser(code, message):
    data = {}
    data['status'] = 'error'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)


def success(like_num):
    data = {}
    data['status'] = 'success'
    data['like_num'] = like_num
    return JsonResponse(data)


def like_change(request):
    user = request.user
    if not user.is_authenticated:
        return errorsponser(400, '未登录')

    content_type = request.GET.get('content_type')
    content_type = ContentType.objects.get(model=content_type)
    object_id = int(request.GET.get('object_id'))
    is_like = request.GET.get('is_like')
    print(is_like)
    if is_like == 'true':
        # 要点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
        if created:
            # 未点赞，进行点赞
            like_count, created = Likes.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.like_num += 1
            like_count.save()
            return success(like_count.like_num)
        else:
            # 以点赞，不能重复点赞
            return errorsponser(402, '已经点赞')
    else:
        # 取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 已点赞，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞总数-1
            like_count, created = Likes.objects.get_or_create(content_type=content_type, object_id=object_id,)
            if not created:
                like_count.like_num -= 1
                like_count.save()
                return success(like_count.like_num)
            else:
                return errorsponser(404, '数据错误')
        else:
            # 没有点赞过，不能取消
            return errorsponser(403, '没有点赞，不能取消')
