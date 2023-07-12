def get_course_image_upload_directory(instance, filename):
    return f'{instance.owner}/courses/{instance.title}/thumbnail/{filename}'


def get_course_file_upload_directory(instance, filename):
    return f'{instance.owner}/courses/{instance.title}/presentation/{filename}'


def get_video_upload_directory(instance, filename):
    return f'{instance.chapter.course.owner}/courses/{instance.chapter.course.title}/chapter_{instance.chapter.title}' \
           f'/videos/{filename}'


def get_chapter_upload_directory(instance, filename):
    return f'{instance.course.owner}/courses/{instance.course.title}/chapter_{instance.title}/{filename}'


def get_category_upload_dir(instance: 'Category', filename):
    return f'categories/{instance.name}/{filename}'


def certificate_upload_dir(instance: "Certificate", filename):
    return f'users/{instance.user.username}/courses/{instance.course.title}/certificate/{filename}'
