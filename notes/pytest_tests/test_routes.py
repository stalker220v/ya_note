# test_routes.py
from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse

@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
# Указываем в фикстурах встроенный клиент.
def test_home_availability_for_anonymous_user(client, name):
    # Адрес страницы получаем через reverse():
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK

# Добавляем к тесту ещё один декоратор parametrize; в его параметры
# нужно передать фикстуры-клиенты и ожидаемый код ответа для каждого клиента.
@pytest.mark.parametrize(
    # parametrized_client - название параметра,
    # в который будут передаваться фикстуры;
    # Параметр expected_status - ожидаемый статус ответа.
    'parametrized_client, expected_status',
    # В кортеже с кортежами передаём значения для параметров:
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture().
    (
            (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
# Этот декоратор оставляем таким же, как в предыдущем тесте.
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
# В параметры теста добавляем имена parametrized_client и expected_status.
def test_pages_availability_for_different_users(
        parametrized_client, name, slug_for_args, expected_status
):
    url = reverse(name, args=slug_for_args)
    # Делаем запрос от имени клиента parametrized_client:
    response = parametrized_client.get(url)
    # Ожидаем ответ страницы, указанный в expected_status:
    assert response.status_code == expected_status

@pytest.mark.parametrize(
    # Вторым параметром передаём note_object(который позднее переименовали в аргс),
    # в котором будет либо фикстура с объектом заметки, либо None.
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и note_object:
def test_redirects(client, name, args):
    login_url = reverse('users:login')

    # # Формируем URL в зависимости от того, передан ли объект заметки:
    # if note_object is not None:
    #     url = reverse(name, args=(note_object.slug,))
    # else:
    #     url = reverse(name)

    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
