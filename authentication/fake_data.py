import random
import tempfile

from faker import Faker
from faker_file.providers.jpeg_file import JpegFileProvider
from faker_file.providers.pdf_file import PdfFileProvider
from faker_file.providers.png_file import PngFileProvider
from faker_file.storages.filesystem import FileSystemStorage

from . import models

fake = Faker()

STORAGE = FileSystemStorage(
    root_path=tempfile.gettempdir(),
    rel_path='faker'
)

fake.add_provider(PdfFileProvider)
fake.add_provider(PngFileProvider)
fake.add_provider(JpegFileProvider)

TEMPLATE = """
{{date}} {{city}}, {{country}}

Hello {{name}},

{{text}} {{text}} {{text}}

{{text}} {{text}} {{text}}

{{text}} {{text}} {{text}}

Address: {{address}}

Best regards,

{{name}}
{{address}}
{{phone_number}}
"""


def get_random_provider():
    res = map(lambda x: fake.jpeg_file if x == 'JPEG' else fake.png_file, ['PNG', 'JPEG'])
    return random.choice(list(res))


def create_random_file() -> (str, str):
    provider = get_random_provider()
    filename = provider(content=fake.text(), storage=STORAGE)
    return STORAGE.abspath(filename), STORAGE.abspath(filename).split('/')[-1]


def create_fake_users():
    username = fake.user_name()
    email = fake.email()
    first_name = fake.first_name()
    last_name = fake.last_name()
    user = models.User(username=username, email=email, first_name=first_name, last_name=last_name)
    user.set_password('rootuser')
    user.save()

    path, filename = create_random_file()
    user.profile_image.save(name=filename, content=open(path, 'rb'))
    return user


if __name__ == "__main__":
    print("hello there")
