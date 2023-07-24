from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import datetime

from admin_dashboard.models import AdminConfig


def is_arabic(text):
    if '\u0600' <= text[0] <= '\u06FF':
        return True
    return False


def generate_certificate(name, course_name: str):
    RES = settings.BASE_DIR / 'certificate_generation' / 'resources'

    arabic_font = ImageFont.truetype(str(RES / 'bold-ar.woff'), 220)
    latin_font = ImageFont.truetype(str(RES / 'bold.ttf'), 220)
    thin_font = ImageFont.truetype(str(RES / 'thin.ttf'), 72)

    if AdminConfig.load().certificate_template.template is None:
        image = Image.open(str(RES / 'vide.png'))
    else:
        image = Image.open(AdminConfig.load().certificate_template.template.path)

    x_res, y_res = image.size

    drawing = ImageDraw.Draw(image)
    drawing.fontmode = 'L'

    font = arabic_font if is_arabic(name) else latin_font

    text_length = drawing.textlength(name, font=font)
    drawing.text(((x_res - text_length) // 2, 1500), name, fill=(83, 83, 173), font=font)
    drawing.text(((x_res - text_length) // 2, 1600 + drawing.textsize(course_name, font=font)[1]),
                 f'Course: {course_name}',
                 fill=(83, 83, 173), font=font)

    drawing.text((1300, 2500), str(datetime.date.today()), fill=(0, 0, 155), font=thin_font)
    return image.resize((x_res // 2, y_res // 2))
