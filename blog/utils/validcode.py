# coding:utf-8
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random


def get_color():
    """
    获取随机颜色
    :return:
    """
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def get_valid_code(request):
    img = Image.new('RGB', (270, 36), color=get_color())  # 生成img对象

    draw = ImageDraw.Draw(img)  # 生成画板

    font_msyh = ImageFont.truetype('static/font/msyh.ttc', size=22)  # 生成字体对象

    # 生成随机数字，字母大小写
    valid_code_str = ""
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_lower = chr(random.randint(95, 122))
        random_upper = chr(random.randint(65, 90))
        random_char = random.choice([random_num, random_lower, random_upper])  # 随机选取一个
        draw.text((i * 50 + 20, 5), random_char, get_color(), font=font_msyh)  # 将文字写入画板对象，坐标，文字内容，颜色，字体
        valid_code_str += random_char

    width = 270
    height = 40
    for i in range(6):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_color())

    # 生成干扰点
    # for i in range(60):
    #     draw.point([random.randint(0, width), random.randint(0, height)], fill=get_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_color())

    # 磁盘操作
    # with open('valid.png', 'wb') as f:
    #     img.save(f, 'png')
    #
    # with open('valid.png', 'rb') as f:
    #     data = f.read()

    request.session['valid_code_str'] = valid_code_str

    # 内存操作
    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()

    return data
