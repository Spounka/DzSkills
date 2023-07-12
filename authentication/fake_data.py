import random
import tempfile

from allauth.account.models import EmailAddress
from django.contrib.auth.models import Group
from faker import Faker
from faker_file.providers.bin_file import BinFileProvider
from faker_file.providers.jpeg_file import JpegFileProvider
from faker_file.providers.png_file import PngFileProvider
from faker_file.storages.filesystem import FileSystemStorage

from . import models

fake = Faker()

STORAGE = FileSystemStorage(
    root_path=tempfile.gettempdir(),
    rel_path='faker'
)

fake.add_provider(PngFileProvider)
fake.add_provider(JpegFileProvider)
fake.add_provider(BinFileProvider)


def get_random_provider():
    res = map(lambda x: fake.jpeg_file if x == 'JPEG' else fake.png_file, ['PNG', 'JPEG'])
    return random.choice(list(res))


def create_fake_users(amount: int = 10):
    users = []
    for _ in range(amount):
        username = fake.user_name()
        email = fake.email()
        first_name = fake.first_name()
        last_name = fake.last_name()
        user = models.User(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password('rootuser')

        user.profile_image.save(name=STORAGE.generate_filename(extension='jpg').split('/')[-1],
                                content=open('/home/spounka/NazihPicture3.jpg', 'rb'))
        email = EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
        email.save()
        users.append(user)
    return users


def create_fake_teachers(amount: int = 10, use_existing: bool = True):
    teachers = []
    if use_existing:
        i = 0
        while i < amount:
            teacher = random.choice(models.User.objects.exclude(groups__name__in=['TeacherGroup'])[0:amount])
            if teacher not in teachers:
                teachers.append(teacher)
                i += 1
    else:
        teachers = create_fake_users(amount)
    for teacher in teachers:
        teacher.groups.add(Group.objects.get(name="TeacherGroup"))
        teacher.save()
    return teachers


if __name__ == "__main__":
    print("hello there")
