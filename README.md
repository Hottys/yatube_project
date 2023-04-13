# Проект спринта
## Автор: Михаил Картавцев
## Описание

Yatube - это социальная сеть с авторизацией, персональными лентами, комментариями и подписками на авторов статей.

## Функционал

- Регистрируется и восстанавливается доступ по электронной почте;
- Добавляются изображения к посту;
- Создаются и редактируются собственные записи;
- Просмотриваются страницы других авторов;
- Комментируются записи других авторов;
- Подписки и отписки от авторов;
- Записи назначаются в отдельные группы;
- Личная страница для публикации записей;
- Отдельная лента с постами авторов на которых подписан пользователь;
- Через панель администратора модерируются записи, происходит управление пользователями и создаются группы.

## Стек:

- Python 3.7.3
- Django==2.2.6
- mixer==7.1.2
- Pillow==9.0.1
- pytest==5.3.5
- pytest-django==3.8.0
- pytest-pythonpath==0.7.3
- requests==2.22.0
- six==1.14.0
- sorl-thumbnail==1.14.0
- Pillow==9.0.1
- django-environ==0.8.1


## Установка

1. Клонировать репозиторий:

   ```python
   git clone https://github.com/Hottys/yatube_project
   ```

2. Перейти в папку с проектом:

   ```python
   cd yatube_project/
   ```

3. Установить виртуальное окружение для проекта:

   ```python
   python -m venv venv
   ```

4. Активировать виртуальное окружение для проекта:

   ```python
   # для OS Lunix и MacOS
   source venv/bin/activate

   # для OS Windows
   source venv/Scripts/activate
   ```

5. Установить зависимости:

   ```python
   python3 -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Выполнить миграции на уровне проекта:

   ```python
   cd yatube
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

7. Зарегистирировать суперпользователя Django:

   ```python
   python3 manage.py createsuperuser

   # адрес панели администратора
   http://127.0.0.1:8000/admin
   ```
8. В папку с проектом, где файл settings.py добавляем файл .env куда прописываем наши параметры:

```bash
SECRET_KEY='Ваш секретный ключ'
ALLOWED_HOSTS='127.0.0.1, localhost'
DEBUG=True
```

9. Не забываем добавить в .gitingore файлы:

```bash
.env
.venv
```

10. Для запуска тестов выполним:

```bash
pytest
```

11. Получим:

```bash
pytest
=================================================== test session starts ===================================================
platform win64 -- Python 3.7.3, pytest-5.3.5, py-1.8.1, pluggy-0.13.1 -- ...\yatube_project\venv\Scripts\python.exe     
django: settings: yatube.settings (from ini)
rootdir: ...\yatube_project, configfile: pytest.ini, testpaths: tests/
plugins: Faker-12.0.1, django-2.2.6, pythonpath-0.7.3
collected 31 items

tests/test_paginator.py::TestGroupPaginatorView::test_group_paginator_view_get PASSED                                [  3%]
tests/test_paginator.py::TestGroupPaginatorView::test_group_paginator_not_in_context_view PASSED                     [  6%]
tests/test_paginator.py::TestGroupPaginatorView::test_index_paginator_not_in_view_context PASSED                     [  9%]
tests/test_paginator.py::TestGroupPaginatorView::test_index_paginator_view PASSED                                    [ 12%]
tests/test_paginator.py::TestGroupPaginatorView::test_profile_paginator_view PASSED                                  [ 16%]
tests/test_about.py::TestTemplateView::test_about_author_tech PASSED                                                 [ 19%] 
tests/test_auth_urls.py::TestAuthUrls::test_auth_urls PASSED                                                         [ 22%]
tests/test_comment.py::TestComment::test_comment_add_view PASSED                                                     [ 25%]
tests/test_comment.py::TestComment::test_comment_add_auth_view PASSED                                                [ 29%]
tests/test_create.py::TestCreateView::test_create_view_get PASSED                                                    [ 32%]
tests/test_create.py::TestCreateView::test_create_view_post PASSED                                                   [ 35%]
tests/test_follow.py::TestFollow::test_follow_not_auth PASSED                                                        [ 38%]
tests/test_follow.py::TestFollow::test_follow_auth PASSED                                                            [ 41%]
tests/test_homework.py::TestPost::test_post_create PASSED                                                            [ 45%]
tests/test_homework.py::TestGroup::test_group_create PASSED                                                          [ 48%]
tests/test_homework.py::TestGroupView::test_group_view PASSED                                                        [ 51%]
tests/test_homework.py::TestCustomErrorPages::test_custom_404 PASSED                                                 [ 54%]
tests/test_homework.py::TestCustomErrorPages::test_custom_500 PASSED                                                 [ 58%] 
tests/test_homework.py::TestCustomErrorPages::test_custom_403 PASSED                                                 [ 61%]
tests/test_post.py::TestPostView::test_index_post_with_image PASSED                                                  [ 64%]
tests/test_post.py::TestPostView::test_index_post_caching PASSED                                                     [ 67%]
tests/test_post.py::TestPostView::test_post_view_get PASSED                                                          [ 70%]
tests/test_post.py::TestPostEditView::test_post_edit_view_get PASSED                                                 [ 74%]
tests/test_post.py::TestPostEditView::test_post_edit_view_author_get PASSED                                          [ 77%]
tests/test_post.py::TestPostEditView::test_post_edit_view_author_post PASSED                                         [ 80%]
tests/test_profile.py::TestProfileView::test_profile_view_get PASSED                                                 [ 83%]
tests/test_comment.py::TestComment::test_comment_model PASSED                                                        [ 87%]
tests/test_follow.py::TestFollow::test_follow PASSED                                                                 [ 90%] 
tests/test_homework.py::TestPost::test_post_model PASSED                                                             [ 93%] 
tests/test_homework.py::TestPost::test_post_admin PASSED                                                             [ 96%] 
tests/test_homework.py::TestGroup::test_group_model PASSED                                                           [100%] 

============================================== 31 passed in 5.86s ==============================================
```

12. Запустить проект локально:

   ```python
   python3 manage.py runserver

   # адрес запущенного проекта
   http://127.0.0.1:8000
   ```

После чего проект будет доступен по адресу http://127.0.0.1:8000

Заходим в http://127.0.0.1:8000/admin и создаем группы и записи.
После чего записи и группы появятся на главной странице.

Автор: Картавцвев Михаил https://github.com/Hottys
