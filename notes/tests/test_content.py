from django.test import TestCase, Client
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse

# Импортируем функцию для получения модели пользователя.
from django.contrib.auth import get_user_model
...
# Дополнительно к News импортируем модель комментария.
from notes.models import Note

# Импортируем класс формы.
from notes.forms import NoteForm

User = get_user_model()

NOTE_TEXT = 'Текст заметки'
NOTE_TEXT_NEW = 'Новый текст заметки'
NOTE_TITLE = 'Заголовок'
SLUG = '23'

# class TestContent(TestCase):
#     # Вынесем ссылку на домашнюю страницу в атрибуты класса.
#     HOME_URL = reverse('notes:home')

#     @classmethod
#     def setUpTestData(cls):
#         all_notes = []
#         for index in range(11):
#             notes = Note(
#                 title=f'Новость {index}',
#                 text='Просто текст.',
#                 slug=f'note{index}'
#             )
#             all_notes.append(notes)
#         Note.objects.bulk_create(all_notes)

class TestNotePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        #cls.author_client = Client()
        # cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.url_list = reverse('notes:list', args=None)
        cls.url_add = reverse('notes:add', args=None)
        all_notes = []
        for index in range(5):
            note = Note(
                title=f'NOTE_TITLE_{index}',
                text=NOTE_TEXT,
                slug=index,
                author=cls.author,
            )
            all_notes.append(note)
        Note.objects.bulk_create(all_notes)

    def test_note_list_author(self):
        """Проверяем, что автору доступны его заметки в списке заметок"""
        self.client.force_login(self.author)
        response = self.client.get(self.url_list)
        object_list = response.context['object_list']
        for note in object_list:
            with self.subTest():
                self.assertIn(note, object_list)

    def test_note_list_reader(self):
        """
        Проверяем, что читателю не доступны чужие заметки в списке заметок
        """
        self.client.force_login(self.reader)
        response = self.client.get(self.url_list)
        object_list = response.context['object_list']
        for note in object_list:
            with self.subTest():
                self.assertNotIn(note, object_list)



    def test_authorized_client_has_form(self):
        """Проверяем, что анониму не доступна форма создания заметки"""
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.url_add)
        self.assertIn('form', response.context)
        # а так же проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], NoteForm)
