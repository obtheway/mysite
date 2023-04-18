from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名')
    password = forms.CharField(label='密码', widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data


class RegForm(forms.Form):
    username = forms.CharField(label='用户名',
                               max_length=20,
                               min_length=3,)
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(attrs={'placeholder':'清输入邮箱'}))
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '输入验证码，点击发送验证码到邮箱'}
        )
    )
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    password_again = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码错误')
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_password_again (self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入密码不一致')
        return password_again


class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(
        label='新的昵称',
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '清输入新的昵称'}
        ),
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()
        if nickname_new == '':
            raise ValueError('新的昵称不能为空')
        return nickname_new


class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        required=False,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '输入验证码，点击发送验证码到邮箱'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
            print('已登录')
        else:
            raise forms.ValidationError('用户尚未登录')
        # 判断用户是否已绑定邮箱
        if self.request.user.email != '':
            print('已绑定邮箱')
            raise forms.ValidationError('已绑定邮箱')
        # 判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码错误')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("该邮箱已绑定")
        print('是否绑定邮箱：',email)
        return email

    # def clean_verification_code(self):
    #     print('是否获取验证码', self.cleaned_data)
    #     verification_code = self.cleaned_data.get('verification', '').strip()
    #     if verification_code == '':
    #         raise forms.ValidationError('验证码不能为空')
    #     print('验证码出错2')
    #     return verification_code


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='旧密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))
    new_password = forms.CharField(label='新密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新密码'}))
    new_password_again = forms.CharField(label='确认密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入新密码'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        print(new_password)
        print(new_password_again)
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致')
        return self.cleaned_data

    def clean_old_password(self):
        # 验证旧密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧密码错误')
        print(old_password)
        return old_password


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(label='用户名',
                               max_length=20,
                               min_length=3, )
    email = forms.EmailField(
        label='邮箱',
        required=False,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击发送验证码到邮箱'}
        )
    )
    new_password = forms.CharField(label='新密码',
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码错误')
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名不存在')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        user = User.objects.get(email=email)
        username = self.cleaned_data.get('username', '')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("邮箱不存在")
        if user.username != username:
            raise forms.ValidationError('用户名与邮箱不匹配')
        return email, username
