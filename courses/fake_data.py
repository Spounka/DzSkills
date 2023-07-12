import random
import tempfile

from faker import Faker
from faker_file.providers.bin_file import BinFileProvider
from faker_file.providers.jpeg_file import JpegFileProvider
from faker_file.providers.pdf_file import PdfFileProvider
from faker_file.providers.png_file import PngFileProvider
from faker_file.storages.filesystem import FileSystemStorage

from authentication.models import User
from . import models

fake = Faker()

STORAGE = FileSystemStorage(
    root_path=tempfile.gettempdir(),
    rel_path='faker'
)

fake.add_provider(PngFileProvider)
fake.add_provider(JpegFileProvider)
fake.add_provider(BinFileProvider)
fake.add_provider(PdfFileProvider)


def get_random_provider():
    res = map(lambda x: fake.jpeg_file if x == 'JPEG' else fake.png_file, ['PNG', 'JPEG'])
    return random.choice(list(res))


def create_fake_hashtags(amount: int = 10):
    hashtags = [models.Hashtag.objects.create(name=f"#{fake.word()}") for _ in range(amount)]
    return hashtags


def create_random_file(text: str = "") -> (str, str):
    provider = get_random_provider()
    content = text if text != "" else fake.text()
    filename = provider(content=content, storage=STORAGE)
    return STORAGE.abspath(filename), STORAGE.abspath(filename).split('/')[-1]


def create_random_pdf(text: str = "") -> (str, str):
    content = text if text != "" else fake.text()
    filename = fake.pdf_file(content=content, storage=STORAGE)
    return STORAGE.abspath(filename), STORAGE.abspath(filename).split('/')[-1]


def create_fake_categories(amount: int = 10):
    categories = []
    for _ in range(amount):
        name = fake.text(max_nb_chars=30)
        description = fake.text(max_nb_chars=300)
        category = models.Category(name=name, description=description)
        path, filename = create_random_file(name)
        category.image.save(name=filename, content=open(path, 'rb'))
        category.save()
        categories.append(category)
    return categories


def create_fake_levels(amount: int = 10):
    levels = [models.Level.objects.create(name=fake.word()) for _ in range(amount)]
    return levels


def create_fake_videos(amount: int = 3, chapter: models.Chapter = None) -> list[models.Video]:
    videos = []
    for _ in range(amount):
        kwargs = {
            "title": fake.text(max_nb_chars=10),
            "description": fake.text(max_nb_chars=150),
        }
        video = models.Video(chapter=chapter, **kwargs)
        video.video.save(name=f"video_{fake.text(max_nb_chars=5)}",
                         content=open('video.webm', 'rb'))
        video.save()
    return videos


def create_fake_chapters(amount: int = 2, course: models.Course = None) -> list[models.Chapter]:
    chapters = []
    for _ in range(amount):
        kwargs = {
            "title": fake.text(max_nb_chars=10),
            "description": fake.text(max_nb_chars=300),
        }
        chapter = models.Chapter(course=course, **kwargs)
        thumbnail_path, thumbnail_name = create_random_file()
        chapter.thumbnail.save(name=thumbnail_name, content=open(thumbnail_path, 'rb'))
        chapter.save()
        chapter.videos.set(create_fake_videos(chapter=chapter))
        chapters.append(chapter)
    return chapters


def create_fake_courses(amount: int = 10, num_chapters: int = 2):
    courses = []
    for _ in range(amount):
        kwargs = {
            "title": fake.text(max_nb_chars=10),
            "description": fake.text(max_nb_chars=300),
            "price": random.uniform(2000, 200_000),
            "course_level": random.choice(models.Level.objects.all()),
            "category": random.choice(models.Category.objects.all()),
            "used_programs": ",".join(fake.words(nb=3)),
            "owner": random.choice(User.objects.filter(groups__name__in=['TeacherGroup'])),
        }
        hashtags = random.sample(list(models.Hashtag.objects.all()), 4)
        course = models.Course(**kwargs)
        thumbnail_path, thumbnail_name = create_random_file()
        course.thumbnail.save(name=thumbnail_name, content=open(thumbnail_path, 'rb'))
        presentation_path, presentation_name = create_random_pdf(kwargs['description'])
        course.presentation_file.save(name=presentation_name, content=open(presentation_path, 'rb'))
        course.save()
        chapters = create_fake_chapters(num_chapters, course=course)
        course.chapters.set(chapters)
        course.hashtags.set(hashtags)
        courses.append(course)

    return courses


def create_fake_rating(ratings_count: int = 10, videos: int = 5, save=False, start_range: int = 1):
    users = list(User.objects.exclude(groups__name__in=['TeacherGroup']))
    videos_list = list(models.Video.objects.all())
    ratings = []
    for _ in range(videos):
        video = random.choice(videos_list)
        for __ in range(ratings_count):
            random_user = random.choice(users)
            ratings.append(models.Rating(student=random_user, video=video, rating=random.uniform(start_range, 5)))
    if save:
        models.Rating.objects.bulk_create(ratings)
    return ratings


if __name__ == "__main__":
    print("hello there")
