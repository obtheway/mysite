from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse

from .models import Comment
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from .form import CommentForm
from django.core.mail import send_mail
# Create your views here.


def update_comment(request):
    # user = request.user
    # text = request.POST.get('text', '')
    # if text == '':
    #     return HttpResponse('评论不能为空')
    #
    # content_type = request.POST.get('content_type', '')
    # object_id = int(request.POST.get('object_id', ''))
    # model_class = ContentType.objects.get(model=content_type).model_class()
    # model_obj = model_class.objects.get(pk=object_id)
    #
    # comment = Comment()
    # comment.user = user
    # comment.text = text
    # comment.content_object = model_obj
    # comment.save()
    #
    # referer = request.META.get('HTTP_REFERER', '/')
    # return redirect(referer)
    referer = request.META.get('HTTP_REFERER', '/')
    comment_form = CommentForm(request.POST, user=request.user)
    if comment_form.is_valid():
        comment = Comment()
        comment.user = request.user
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user

        # 保存评论
        comment.save()

        # 发送邮件
        comment.send_mail()

        # return redirect(referer)
        data = {}
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.get_nickname_or_username()
        data['comment_time'] = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
        data['text'] = comment.text
        if not parent is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
        return JsonResponse(data)
    else:
        # return HttpResponse('评论出错')
        data = {}
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
        return JsonResponse(data)
