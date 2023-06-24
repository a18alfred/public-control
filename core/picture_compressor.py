from django.conf import settings
import sys
# Модули для сжатия фото
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
from django.core.files.base import File
from django.core.exceptions import ValidationError


def compress_picture(uploaded_picture):
    """
    Функция сжатия фотографий. Функция сжимает фото, уменьшает размер до 1024 (сохраняя пропорции) по ширине и сохраняет в JPG
    """
    picture_temporary = Image.open(uploaded_picture).convert("RGB")

    output_io_stream = BytesIO()
    width, height = picture_temporary.size
    new_width = settings.SAVED_PICTURE_WIDTH
    new_height = int(new_width * height / width)
    picture_temporary = picture_temporary.resize((new_width, new_height))
    picture_temporary.save(output_io_stream, format='JPEG', quality=settings.SAVED_PICTURE_QUALITY)
    output_io_stream.seek(0)
    uploaded_picture = InMemoryUploadedFile(output_io_stream, 'ImageField',
                                            "%s.jpg" % uploaded_picture.name.split('.')[0],
                                            'image/jpeg', sys.getsizeof(output_io_stream), None)
    return uploaded_picture


def create_test_image(name='test.png', ext='png', size=(50, 50), color=(256, 0, 0)):
    file_obj = BytesIO()
    image = Image.new("RGBA", size=size, color=color)
    image.save(file_obj, ext)
    file_obj.seek(0)
    return File(file_obj, name=name)


def validate_image(image):
    file_size = image.size
    if file_size > settings.SAVED_PICTURE_MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError("Максимальный размер файла %s MB" % settings.SAVED_PICTURE_MAX_FILE_SIZE_MB)
