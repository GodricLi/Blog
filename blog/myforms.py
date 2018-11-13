# coding:utf-8

from django import forms
from django.forms import widgets
from blog.models import UserInfo
from django.core.exceptions import ValidationError


class UserForm(forms.Form):
    name = forms.CharField(max_length=32, label='用户名',
                           error_messages={'required': '用户名不能为空'},
                           widget=widgets.TextInput(attrs={'class': 'form-control'}))
    pwd = forms.CharField(max_length=32, label='密码', widget=widgets.PasswordInput(attrs={"class": "form-control"})
                          , error_messages={'required': '密码不能为空'})
    re_pwd = forms.CharField(max_length=32, label='确认密码', widget=widgets.PasswordInput(attrs={"class": "form-control"})
                             , error_messages={'required': '请再次确认密码'})
    email = forms.EmailField(label='邮箱', widget=widgets.EmailInput(attrs={"class": "form-control"}),
                             error_messages={'required': '邮箱不能为空'})

    def clean_name(self):
        """
        用户名钩子：校验name字段
        :return:
        """
        val = self.cleaned_data.get('name')

        user = UserInfo.objects.filter(username=val).first()

        if not user:
            return val
        else:
            raise ValidationError('该用户名已注册')

    def clean(self):
        """
        全局钩子
        :return:
        """
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')

        if pwd and re_pwd:
            if pwd == re_pwd:
                return self.cleaned_data
            else:
                raise ValidationError("两次密码不一致")
        else:
            return self.cleaned_data
