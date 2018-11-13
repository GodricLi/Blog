# coding:utf-8


from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth
from blog import models
from django.shortcuts import render

register = template.Library()


@register.inclusion_tag('classification.html')  # 自定义过滤器，将下面函数return的数据加载到指定的html文件
def get_classification_style(username):
    user = models.UserInfo.objects.filter(username=username).first()

    blog = user.blog

    # 查询当前站点的每一个分类对应名称对应的文章数
    cate_list = models.Category.objects.filter(blog=blog).values('pk').annotate(
        c=Count('article__title')).values_list(
        'title', 'c')

    # 查询当前站点的每一个标签名称及对应的文章数
    tag_list = models.Tag.objects.filter(blog=blog).values('pk').annotate(c=Count('article')).values_list(
        'title', 'c')

    # 查询当前站点每一个年月对应的文章数
    date_list = models.Article.objects.filter(user_id=user.pk).annotate(month=TruncMonth('create_time')).values('month').annotate(
        c=Count('nid')).values_list('month', 'c')

    return {"cate_list": cate_list, "tag_list": tag_list, "date_list": date_list, 'username': user, 'blog': blog}
