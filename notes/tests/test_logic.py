# notes/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    # Текст комментария понадобится в нескольких местах кода,
    # поэтому запишем его в атрибуты класса.
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок'
    SLUG = '23'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add', args=None)
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.user = User.objects.create(username='Мимо Проходил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': cls.NOTE_TITLE,
            'slug': cls.SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверяем отправку формы создания заметки гостем"""
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Проверяем отправку формы создания заметки юзером"""
        # Совершаем запрос через авторизованный клиент.
        self.auth_client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(notes_count, 1)
        # Получаем объект комментария из базы.
        note = Note.objects.get()
        # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.author, self.user)

    def test_dabl_slug(self):
        """Проверяем уникальность slug"""
        self.note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.SLUG,
            author=self.user
        )
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG + WARNING
        )

    def test_auto_slug(self):
        self.note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            author=self.user
        )
        note1 = Note.objects.get()
        self.assertEqual(note1.slug, slugify(self.form_data['title']))


