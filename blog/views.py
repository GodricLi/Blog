import threading
import os
import json
from bs4 import BeautifulSoup

from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.core.mail import send_mail

from BBSblog import settings
from blog.utils.validcode import get_valid_code
from blog.myforms import UserForm
from blog.models import UserInfo
from blog import models

# Create your views here.


def login(request):
    """
    登陆页面
    :param request:
    :return:
    """
    if request.method == "POST":
        response = {'user': None, 'msg': None}  # 返回给ajax的data

        user = request.POST.get('user')
        pwd = request.POST.get('pwd')

        valid_code = request.POST.get('valid_code')
        valid_code_str = request.session.get('valid_code_str')
        if valid_code.upper() == valid_code_str.upper():
            user = auth.authenticate(username=user, password=pwd)
            if user:
                auth.login(request, user)  # 当前登录用户
                response['user'] = user.username
            else:
                response['msg'] = 'wrong username or password!'

        else:
            response['msg'] = 'valid code error!'

        return JsonResponse(response)  # 返回序列化数据

    return render(request, 'login.html')


def valid_code_img(request):
    """
    图形验证码
    :param request:
    :return:
    """
    data = get_valid_code(request)

    return HttpResponse(data)


def index(request):
    """
    主页视图函数
    website home page
    :param request:
    :return:
    """
    article_list = models.Article.objects.all()

    # 分页器
    paginator = Paginator(article_list, 5)
    current_page_num = int(request.GET.get('page', 1))  # 当前页

    if current_page_num - 5 < 1:
        page_range = range(1, paginator.num_pages + 1)
    elif current_page_num + 5 > paginator.num_pages:
        page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
    else:
        page_range = range(current_page_num - 5, current_page_num + 6)

    try:
        current_page_data = paginator.page(current_page_num)  # 当前页数据
    except EmptyPage as e:
        current_page_data = paginator.page(1)
    except PageNotAnInteger as e:
        current_page_data = paginator.page(1)

    return render(request, 'index.html', locals())


def register(request):
    """
    注册视图函数
    register
    :param request:
    :return:
    """
    if request.is_ajax():
        form = UserForm(request.POST)
        response = {"user": None, "msg": None}

        if form.is_valid():  # 数据校验成功
            response["user"] = form.cleaned_data.get("name")
            # 生成用户记录
            user = form.cleaned_data.get("name")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar_obj = request.FILES.get("avatar")

            extra = {}
            if avatar_obj:  # 如果avatar_obj为true那么字段avatar就为avatar_obj，否则为默认的
                extra["avatar"] = avatar_obj
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)
        else:
            response["msg"] = form.errors

        return JsonResponse(response)

    form = UserForm()

    return render(request, 'register.html', locals())


def logout(request):
    """
    注销视图函数
    logout
    :param request:
    :return:
    """
    auth.logout(request)

    return redirect('/index/')


def home_site(request, username, **kwargs):
    """
    个人站点页面
    personal site
    :param request:
    :param username:
    :param kwargs:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'not_found.html')
    else:
        blog = user.blog

        article_list = models.Article.objects.filter(user=user)

        if kwargs:
            # kwargs不为空 说明个人站点后面有路径参数传入，个人站点跳转
            condition = kwargs.get('condition')
            param = kwargs.get('param')

            if condition == 'tag':
                article_list = article_list.filter(tags__title=param)
            elif condition == 'category':
                article_list = article_list.filter(category__title=param)
            else:
                year, moth = param.split('-')
                article_list = article_list.filter(create_time__year=year, create_time__month=moth)

        else:  # kwargs为空说明路径为个人站点
            article_list = article_list

        # 每一个后的表模型.objects.values("pk").annotate(x=聚合函数(关联表__统计字段)).values('统计字段',"x")
        # 查询每一个分类名称以及对应的文章数
        # ret = models.Category.objects.values('pk').annotate(c=Count('article__title')).values('title', 'c')
        #
        # # 查询当前站点的每一个分类对应名称对应的文章数
        # cate_list = models.Category.objects.filter(blog=blog).values('pk').annotate(
        #     c=Count('article__title')).values_list(
        #     'title', 'c')
        # # print(cate_list)
        #
        # # 查询当前站点的每一个标签名称及对应的文章数
        # tag_list = models.Tag.objects.filter(blog=blog).values('pk').annotate(c=Count('article')).values_list(
        #     'title', 'c')
        # # print('tag', tag_list)
        #
        # # 查询当前站点每一个年月对应的文章数
        # date_list = models.Article.objects.annotate(month=TruncMonth('create_time')).values('month').annotate(
        #     c=Count('nid')).values_list('month', 'c')
        # # print(date_list)

        return render(request, 'home_site.html', locals())


def article_detail(request, username, article_id):
    """
    文章详细页面试图
    article detail view

    :param request:
    :param username:
    :param article_id:
    :return:
    """

    user = UserInfo.objects.filter(username=username).first()

    blog = user.blog

    article_obj = models.Article.objects.filter(pk=article_id).first()

    comment_list = models.Comment.objects.filter(article_id=article_id)

    return render(request, 'article_detail.html', locals())


def like(request):
    """
    点赞视图函数
    give the thumbs-up
    :param request:
    :return:
    """
    user_id = request.user.pk  # 点赞人即是当前登录人
    article_id = request.POST.get('article_id')
    is_up = json.loads(request.POST.get('is_up'))  # 字符串'true'，反序列化为bool

    obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()

    response = {"status": True, }
    if not obj:
        models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
        up_down = models.Article.objects.filter(pk=article_id)
        if is_up:
            up_down.update(up_count=F('up_count') + 1)
        else:
            up_down.update(down_count=F('down_count') + 1)
    else:
        response["status"] = False
        response["tips"] = obj.is_up

    return JsonResponse(response)


def comment(request):
    print(request.POST)

    user_id = request.user.pk
    article_id = request.POST.get('article_id')
    comment = request.POST.get('comment')
    pid = request.POST.get('pid')
    article_obj = models.Article.objects.filter(pk=article_id).first()
    # 事务操作
    with transaction.atomic():
        comment_obj = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=comment,
                                                    parent_comment_id=pid)
        models.Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') + 1)

    response = {}
    response['create_time'] = comment_obj.create_time.strftime("%Y-%m-%d %X")  # 转化成日期格式
    response['comment'] = comment_obj.content
    response['username'] = request.user.username

    # 评论内容发送邮件
    # t = threading.Thread(target=send_mail, args=(
    #     '您的文章%s新增一条评论' % article_obj.title,
    #     comment,
    #     settings.EMAIL_HOST_USER,
    #     ['635434705@qq.com']
    # ))
    # t.start()

    return JsonResponse(response)


def get_comment_tree(request):
    article_id = request.GET.get('article_id')
    data = list(models.Comment.objects.filter(article_id=article_id).values('pk', 'content', 'parent_comment'))
    # 转化成列表

    return JsonResponse(data, safe=False)  # JsonResponse转行非字典需要设置safe=False


@login_required
def blog_backend(request):
    """
    后台管理
    :param request:
    :return:
    """
    user = request.user
    article_list = models.Article.objects.filter(user=user).all()

    # 分页器
    paginator = Paginator(article_list, 5)
    current_page_num = int(request.GET.get('page', 1))  # 当前页

    if current_page_num - 5 < 1:
        page_range = range(1, paginator.num_pages + 1)
    elif current_page_num + 5 > paginator.num_pages:
        page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
    else:
        page_range = range(current_page_num - 5, current_page_num + 6)

    try:
        current_page_data = paginator.page(current_page_num)  # 当前页数据
    except EmptyPage as e:
        current_page_data = paginator.page(1)
    except PageNotAnInteger as e:
        current_page_data = paginator.page(1)

    return render(request, 'blog_backend.html', locals())


@login_required
def add_article(request):
    """
    添加文章
    :param request:
    :return:
    """
    if request.method == 'POST':
        user = request.user
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')  # 解析html

        # 过滤script标签
        for tag in soup.find_all():
            if tag.name == 'script':
                tag.decompose()

        desc = soup.text[0:150]  # 截取文本内容
        models.Article.objects.create(title=title, content=str(soup), desc=desc, user=user)

        return redirect('/blog_backend/')

    return render(request, 'add_article.html', locals())


def editor_article(request, article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    if request.method == 'POST':
        user = request.user
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')  # 解析html

        # 过滤script标签
        for tag in soup.find_all():
            if tag.name == 'script':
                tag.decompose()

        desc = soup.text[0:150]  # 截取文本内容
        models.Article.objects.filter(pk=article_id).update(title=title, content=str(soup), desc=desc, user=user)

        return redirect('/blog_backend/')
    return render(request, 'editor_article.html', locals())


@login_required
def delete_article(request, article_id):
    """
    删除文章
    :param request:
    :param article_id:
    :return:
    """
    models.Article.objects.filter(pk=article_id).delete()
    return redirect('/blog_backend/')


def upload(request):
    """
    上传文件
    :param request:
    :return:
    """
    print(request.FILES)  # 获取文件相关信息 <MultiValueDict: {'imgFile': [<InMemoryUploadedFile: dengji.jpg (image/jpeg)>]}>

    img = request.FILES.get('imgFile')  # 获取传入的文件对象
    path = os.path.join(settings.MEDIA_ROOT, 'add_article_img', img.name)
    with open(path, 'wb')as f:
        for line in img:
            f.write(line)

    response = {
        "error": 0,
        "url": "/media/add_article_img/%s" % img.name  # 将浏览器能够访问的文件路径返回（media/....
    }
    json_response = json.dumps(response)

    return HttpResponse(json_response)
