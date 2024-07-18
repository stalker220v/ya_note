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

NOTE_TEXT = 'Текст заметки'
NOTE_TEXT_NEW = 'Новый текст заметки'
NOTE_TITLE = 'Заголовок'
SLUG = '23'

class TestNoteCreation(TestCase):
    # Текст комментария понадобится в нескольких местах кода,
    # поэтому запишем его в атрибуты класса.
    # NOTE_TEXT = 'Текст заметки'
    # NOTE_TITLE = 'Заголовок'
    # SLUG = '23'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add', args=None)
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.user = User.objects.create(username='Мимо Проходил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {
            'text': NOTE_TEXT,
            'title': NOTE_TITLE,
            'slug': SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверяем отправку создания заметки гостем"""
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Проверяем отправку создания заметки залогиненым юзером"""
        # Совершаем запрос через авторизованный клиент.
        self.auth_client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(notes_count, 1)
        # Получаем объект комментария из базы.
        note = Note.objects.get()
        # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
        self.assertEqual(note.text, NOTE_TEXT)
        self.assertEqual(note.title, NOTE_TITLE)
        self.assertEqual(note.author, self.user)

    def test_dabl_slug(self):
        """Проверяем уникальность slug"""
        self.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=SLUG,
            author=self.user
        )
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=SLUG + WARNING
        )

    def test_auto_slug(self):
        """Проверяем автоматическое создание slug"""
        self.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            author=self.user
        )
        note1 = Note.objects.get()
        self.assertEqual(note1.slug, slugify(self.form_data['title']))

class TestNoteEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            author=cls.author,
        )
        cls.url_success = reverse('notes:success', args=None)
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': NOTE_TEXT_NEW,
            'title': NOTE_TITLE
        }

    def test_author_delete_note(self):
        """Проверяем удаление автором"""
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        # Считаем количество комментариев в системе.
        note_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(note_count, 0)

    def test_reader_delete_note(self):
        """Проверяем удаление гостем"""
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.url_delete)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что комментарий по-прежнему на месте.
        note_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(note_count, 1)

    def test_author_edit_note(self):
        """Проверяем редактирование автором"""
        # Выполняем запрос на редактирование от имени автора комментария.
        response = self.author_client.post(self.url_edit, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.url_success)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст комментария соответствует обновленному.
        self.assertEqual(self.note.text, NOTE_TEXT_NEW)

    def test_reader_edit_note(self):
        """Проверяем редактирование гостем"""
        # Выполняем запрос на редактирование от имени автора комментария.
        response = self.reader_client.post(self.url_edit, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст комментария соответствует старому.
        self.assertEqual(self.note.text, NOTE_TEXT)