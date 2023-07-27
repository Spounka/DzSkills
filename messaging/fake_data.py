from . import models, services
import tempfile
from authentication.models import User
from courses.models import Course
from faker import Faker
from faker_file.providers.pdf_file import PdfFileProvider
from faker_file.providers.png_file import PngFileProvider
from faker_file.storages.filesystem import FileSystemStorage
import random

fake = Faker()

STORAGE = FileSystemStorage(
    root_path=tempfile.gettempdir(),
    rel_path='faker'
)

fake.add_provider(PdfFileProvider)
fake.add_provider(PngFileProvider)

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
    res = map(lambda x: fake.pdf_file if x == 'PDF' else fake.png_file, ['PNG', 'PDF'])
    return random.choice(list(res))


def create_random_file() -> (str, str):
    provider = get_random_provider()
    filename = provider(content=fake.text(), storage=STORAGE)
    return STORAGE.abspath(filename), STORAGE.abspath(filename).split('/')[-1]


def create_course_fake_messages(amount=10, course: int = 1, sender_id: int = 1, recipient_id: int = 2,
                                vary_courses: bool = False):
    sender = User.objects.filter(pk=sender_id).first()
    recipient = User.objects.filter(pk=recipient_id).first()
    course = Course.objects.filter(pk=course).first()
    if not sender:
        sender = User.objects.last()
    if not recipient:
        recipient = User.objects.exclude(sender).last()
    if not course:
        course = Course.objects.last()

    for _ in range(amount):
        message = services.MessageService.create(course=course,
                                                 sender=sender,
                                                 recipient=recipient,
                                                 content=fake.text())
        files = [models.MessageFile().generate(message, create_random_file()) for _ in range(4)]
        message.messagefile_set.set(files)
        sender, recipient = recipient, sender
        if vary_courses:
            course = random.choice(Course.objects.all().exclude(course))


def create_fake_messages(conversations: int = 10, amount: int = 10, ):
    students = (User.objects.exclude(groups__name__in=['AdminGroup', 'TeacherGroup']).all())
    teachers = (User.objects.filter(groups__name__in=['TeacherGroup'])).all()
    for __ in range(conversations):
        student: User = random.choice(list(students))
        teacher: User = random.choice(list(teachers.exclude(username=student.username)))
        course: Course = random.choice(list(teacher.courses.all()))
        sender, recipient = student, teacher
        for _ in range(amount):
            message = services.MessageService.create(course=course,
                                                     sender=sender,
                                                     recipient=recipient,
                                                     content=fake.text())
            files = [models.MessageFile().generate(message, create_random_file()) for ___ in range(4)]
            message.messagefile_set.set(files)
            sender, recipient = recipient, sender
