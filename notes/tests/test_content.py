from django.test import TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
# Импортируйте нужные классы. 
from datetime import datetime, timedelta
# Допишите новый импорт.
from django.utils import timezone

# Импортируем функцию для получения модели пользователя.
from django.contrib.auth import get_user_model
...
# Дополнительно к News импортируем модель комментария.
from notes.models import Note

# Импортируем класс формы.
from notes.forms import NoteForm

User = get_user_model()


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

class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        # cls.notes = Note.objects.create(
        #     title='Тестовая', text='Просто текст.'
        # )
        # Сохраняем в переменную адрес страницы с новостью:
        
        # cls.author = User.objects.create(username='Комментатор')

        cls.author = User.objects.create(username='Got')
        # cls.note = Note.objects.create(
        #     title='pfv', text='uofyyt', slug='23', author=cls.author
        # )
        cls.add_url = reverse('notes:add', args=None)
        # Запоминаем текущее время:
        # now = datetime.now()
        # Получите текущее время при помощи утилиты timezone.
        # now = timezone.now()
        # Создаём комментарии в цикле.
        # for index in range(10):
        #     # Создаём объект и записываем его в переменную.
        #     note = Note.objects.create(
        #         title='pfv', text='uofyyt', slug='23', author=cls.author
        #         )
        #     # Сразу после создания меняем время создания комментария.
        #     comment.created = now + timedelta(days=index)
        #     # И сохраняем эти изменения.
        #     comment.save()         

    # def test_comments_order(self):
    #     response = self.client.get(self.detail_url)
    #     # Проверяем, что объект новости находится в словаре контекста
    #     # под ожидаемым именем - названием модели.
    #     self.assertIn('notes', response.context)
    #     # Получаем объект новости.
    #     notes = response.context['notes']
    #     # Получаем все комментарии к новости.
    #     all_comments = notes.comment_set.all()
    #     # Собираем временные метки всех новостей.
    #     all_timestamps = [comment.created for comment in all_comments]
    #     # Сортируем временные метки, менять порядок сортировки не надо.
    #     sorted_timestamps = sorted(all_timestamps)
    #     # Проверяем, что временные метки отсортированы правильно.
    #     self.assertEqual(all_timestamps, sorted_timestamps)

# Для авторизованного пользователя на странице новости должна быть видна форма комментариев,
# а для анонимного — нет. Как именно рендерится HTML-форма и что там отображается — мы
# проверять не будем, но можем проверить, есть ли объект form в словаре контекста и относится 
# ли этот объект  к нужному классу.    
#     def test_anonymous_client_has_no_form(self):
#         # первый тест проверит, что при запросе анонимного пользователя форма не передаётся
#         # в словаре контекста.
#         response = self.client.get(self.add_url)
#         self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        # а так же проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], NoteForm)
