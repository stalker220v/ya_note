# notes/tests/test_routes.py
# Импортируем класс HTTPStatus.
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
# Импортируем функцию reverse().
from django.urls import reverse

from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Got')
        cls.reader = User.objects.create(username='Гость')
        cls.note = Note.objects.create(
            title='pfv', text='uofyyt', slug='1p', author=cls.author
        )

    def test_pages(self):
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.pk)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
