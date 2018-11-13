"""BBSblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from blog import views
from django.views.static import serve
from BBSblog import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('logout/', views.logout),
    path('index/', views.index),

    # 验证码
    path('get_valid_img/', views.valid_code_img),
    # 注册页面
    path('register/', views.register),

    # 点赞页面
    path('like/', views.like),
    # 评论
    path('comment/', views.comment),
    # 评论树
    path('get_comment_tree/', views.get_comment_tree),

    # 后台管理
    path('blog_backend/', views.blog_backend),
    # 添加文章
    path('add_article/', views.add_article),
    # 删除文章
    re_path('(?P<article_id>\d+)/delete/$', views.delete_article),
    # 编辑文章
    re_path('(?P<article_id>\d+)/editor/$', views.editor_article),

    # 上传文件
    path('upload/', views.upload),
    # media配置,可以访问media路径
    re_path(r'media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),

    # 个人站点页面
    re_path('^(?P<username>\w+)$/', views.home_site),

    # 文章详细页
    re_path('^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),

    # 个人站点的跳转页面
    re_path('^(?P<username>\w+)/(?P<condition>|tag|category|archive)/(?P<param>.*)/$', views.home_site),

    re_path('^$', views.index),
]
