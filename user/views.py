from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import send_mail
import string
import random
import time
from .form import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from .models import Profile


def logins(request):
    # # next = request.POST.get('next')
    # username = request.POST.get('username')
    # password = request.POST.get('password')
    # referer = request.META.get('HTTP_REFERER', '/')
    # user = authenticate(username=username, password=password)
    # if user is not None:
    #     login(request, user)
    #     # return HttpResponseRedirect(next)
    #     return redirect(referer)
    # else:
    #     return render(request, 'error.html')
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            login(request, user)
            return redirect(request.GET.get('from', '/'))
    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)


def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            user = User.objects.create_user(username, email, password)
            user.save()
            # 清除session
            del request.session['bind_email_code']
            '''
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            user.save()
            '''
            user =authenticate(username=username, password=password)
            login(request, user)
            return redirect(request.GET.get('from', '/'))
    else:
        reg_form = RegForm()

    context = {}
    context['reg_form'] = reg_form
    return render(request, 'register.html', context)


def logout_view(request):
    logout(request)
    return redirect('/')


def info(request):
    context = {}
    return render(request, 'info.html', context)


def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()
    context = {}
    context['form'] = form
    context['title'] = '修改昵称'
    context['submit_text'] = '确认修改'
    return render(request, 'form.html', context)


def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        print('if判断')
        form = BindEmailForm(request.POST, request=request)
        # print(type(form))
        if form.is_valid():
            print('第二层·if')
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            del request.session['bind_email_code']
            print('保存邮箱')
            return redirect(redirect_to)
        else:
            print('第二层if失败')
    else:
        form = BindEmailForm()
    context = {}
    context['form'] = form
    context['title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    print('bind结束')
    return render(request, 'bind_email.html', context)


def send_verification_code(request):
    data = {}
    email = request.GET.get('email', '')
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))

        print(code)
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'error'
        else:
            request.session['bind_email_code'] = code
            request.session['send_code_time'] = now
            send_mail(
                '绑定邮箱',  # 邮箱主题
                '验证码：%s' % code,  # 邮件内容
                '875600228@qq.com',  # 发送邮箱的地址
                [email],  # 接收邮箱，列表形式，可游戏多个邮箱
                fail_silently=False,
            )
            data['status'] = 'success'
    else:
        data['status'] = 'error'
    return JsonResponse(data)


def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            password = form.cleaned_data.get('new_password', '')
            user = request.user
            user.set_password(password)
            user.save()
            logout(request)
            return redirect(reverse('home'))
    else:
        form = ChangePasswordForm()

    context = {}
    context['form'] = form
    context['form_title'] = '修改密码'
    context['submit_text'] = '确认修改密码'
    return render(request, 'form.html', context)


def forgot_password(request):
    redirect_to = reverse('login')
    if request.method == 'POST':
        print('if判断')
        form = ForgotPasswordForm(request.POST, request=request)
        # print(type(form))

        if form.is_valid():
            username = form.cleaned_data.get('username', '')
            new_password = form.cleaned_data.get('new_password', '')
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            del request.session['bind_email_code']
            print('保存邮箱')
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()
    context = {}
    context['form'] = form
    context['title'] = '重置密码'
    context['submit_text'] = '重置密码'
    return render(request, 'forgot_password.html', context)


