from django.test import TestCase
from django.conf import settings
from core.picture_compressor import create_test_image, compress_picture
from PIL import Image


class PictureCompressorTestCase(TestCase):

    def test_picture_compressor(self):
        """
        Тестируем сжатие фотографии, конвертацию в JPEG и изменение размера
        """
        test_image = create_test_image(name='test1.png')
        compressed_image = compress_picture(test_image)
        self.assertTrue(compressed_image)
        image = Image.open(compressed_image)
        width, height = image.size
        self.assertEqual(width, settings.SAVED_PICTURE_WIDTH)
        self.assertEqual('JPEG', image.format)
