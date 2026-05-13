# TeamFinder

Дипломный проект Яндекс Практикума: платформа для поиска команды и pet-проектов.
Реализован **вариант 1** — «Избранное» и фильтрация пользователей по 4 критериям.

Стек: **Python 3.10+**, **Django 5.2**, **PostgreSQL 16**, **Pillow**, **Docker Compose**.

---

## 1. Подготовка окружения

### 1.1. Виртуальное окружение и зависимости

```powershell
python -m venv venv
venv\Scripts\Activate.ps1            # Windows PowerShell
# или: source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

### 1.2. Файл `.env`

Скопируйте пример и при необходимости поправьте значения:

```powershell
Copy-Item .env_example .env          # Windows
# или: cp .env_example .env         # Linux/Mac
```

Обязательно проверьте, что в `.env` стоит `TASK_VERSION=1` (используется набор шаблонов `templates_var1`).

| Переменная             | Назначение                                            |
|------------------------|-------------------------------------------------------|
| `DJANGO_SECRET_KEY`    | Секретный ключ Django                                 |
| `DJANGO_DEBUG`         | `True` в разработке, `False` в продакшене             |
| `DJANGO_ALLOWED_HOSTS` | Список разрешённых хостов через запятую               |
| `POSTGRES_DB`          | Имя БД                                                |
| `POSTGRES_USER`        | Пользователь БД                                       |
| `POSTGRES_PASSWORD`    | Пароль                                                |
| `POSTGRES_HOST`        | `localhost` при локальной разработке                  |
| `POSTGRES_PORT`        | Порт Postgres (по умолчанию `5432`)                   |
| `TASK_VERSION`         | Номер варианта задания — для этого проекта **должен быть `1`** |

### 1.3. PostgreSQL через Docker Compose

```bash
docker compose up -d
```

Контейнер `teamfinder_db` поднимет Postgres 16 и пробросит порт `${POSTGRES_PORT}` (по умолчанию 5432) на хост. Данные хранятся в volume `postgres_data` и не теряются между перезапусками.

Остановить:

```bash
docker compose down
```

### 1.4. Миграции и запуск

```bash
python manage.py migrate
python manage.py seed_demo            # добавит тестовых пользователей и проекты
python manage.py createsuperuser      # опционально, для админки /admin/
python manage.py runserver
```

Готово — открывайте [http://localhost:8000](http://localhost:8000).

---

## 2. Тестовые данные

Управляется командой `seed_demo`:

```bash
python manage.py seed_demo            # создаёт 4 пользователей и 5 проектов
python manage.py seed_demo --reset    # удаляет демо и пересоздаёт
```

Тестовые учётные записи (пароль у всех — `password`):

| Email              | Имя              | Проекты                            |
|--------------------|------------------|------------------------------------|
| `maria@yandex.ru`  | Мария Иванова    | TeamFinder, PetShop API            |
| `ivan@yandex.ru`   | Иван Петров      | Async Chat                         |
| `olga@yandex.ru`   | Ольга Сидорова   | Дизайн-система TeamFinder          |
| `alex@yandex.ru`   | Алексей Кузнецов | DevOps Toolbox                     |

Между ними настроены связи (участие, избранное), чтобы продемонстрировать фильтры на странице `/users/list/`.

---

## 3. Тесты и линтинг

### Pytest (использует SQLite in-memory, Postgres для тестов не нужен)

```bash
pytest
```

В наборе 36 тестов: модели, формы, валидация телефона/GitHub, ключевые view, права доступа, пагинация, JSON-эндпоинты избранного и участия.

### flake8

Конфигурация в `setup.cfg` (длина строки 100, исключения для миграций и шаблонов).

```bash
flake8 users projects team_finder tests
```

---

## 4. Структура проекта

```
team_finder/        # настройки Django, корневой urls.py
users/              # кастомная модель User, формы, views, авто-аватар, seed
projects/           # модель Project, формы, views
templates_var1/     # HTML-шаблоны варианта 1
static/             # CSS/JS/шрифты/SVG
media/              # пользовательские аватары (создаётся автоматически)
tests/              # pytest-тесты
```

### Кастомная модель `users.User`

Идентификация по `email`. Поля: `name`, `surname`, `avatar`, `phone` (уникальный, формат `8XXXXXXXXXX` / `+7XXXXXXXXXX`, при сохранении нормализуется в `+7…`), `github_url` (с валидацией, что хост — `github.com`), `about`, `favorites` (M2M к `Project`). При первом `save()` без аватара автоматически генерируется PNG-картинка `256×256` с первой буквой имени на случайном цветном фоне.

### Модель `projects.Project`

Поля строго по ТЗ: `name`, `description`, `owner`, `created_at`, `github_url`, `status` (`open`/`closed`), `participants` (M2M). Сортировка по `-created_at, -id`, индексы по `created_at` и `status`. Связи названы `user.owned_projects` и `user.participated_projects` — как требует ТЗ.

---

## 5. URL-карта

| Метод | Путь                                          | Назначение                                   |
|-------|-----------------------------------------------|----------------------------------------------|
| GET   | `/`                                           | Редирект на `/projects/list/`                |
| GET   | `/projects/list/`                             | Список проектов (12 на странице)             |
| GET   | `/projects/<id>/`                             | Страница проекта                             |
| GET/POST | `/projects/create-project/`                | Создание проекта (только авторизованные)     |
| GET/POST | `/projects/<id>/edit/`                     | Редактирование (только автор/админ)          |
| POST  | `/projects/<id>/complete/`                    | Завершить проект (JSON ответ)                |
| POST  | `/projects/<id>/toggle-participate/`          | Присоединиться/покинуть (JSON ответ)         |
| POST  | `/projects/<id>/toggle-favorite/`             | Добавить/убрать из избранного (JSON ответ)   |
| GET   | `/projects/favorites/`                        | Избранные проекты пользователя               |
| GET/POST | `/users/register/`                         | Регистрация                                  |
| GET/POST | `/users/login/`                            | Вход                                         |
| GET   | `/users/logout/`                              | Выход                                        |
| GET   | `/users/list/`                                | Список участников + фильтры (12 на странице) |
| GET   | `/users/<id>/`                                | Профиль пользователя                         |
| GET/POST | `/users/edit-profile/` и `/users/<id>/edit/` | Редактирование своего профиля             |
| GET/POST | `/users/change-password/`                  | Смена пароля                                 |
| GET   | `/admin/`                                     | Django-админка                               |

---

## 6. Особенности реализации

- **Регистрация** просит только `name`/`surname`/`email`/`password`. Поле `phone` обязательно на уровне БД, поэтому при регистрации проставляется уникальный placeholder в формате `+7XXXXXXXXXX`, который пользователь меняет на свой при редактировании профиля.
- **Валидация телефона**: на форме принимаются оба формата (`8…` и `+7…`), при сохранении приводятся к единому `+7…`. Это обеспечивает уникальность даже для одного и того же номера в разных форматах.
- **Валидация GitHub**: проверяется схема `http(s)://` и хост `github.com` (поддомены разрешены).
- **Тестовые настройки** (`team_finder/test_settings.py`) переключают БД на SQLite in-memory, чтобы тесты прогонялись без Postgres/Docker.
- **Шаблоны var1 ожидают** контекст вида `{"projects": …}`, `{"participants": …, "active_filter": …}`, `{"user": …}`, `{"project": …}`, `{"form": …, "is_edit": …}` — именно так view и формируют контекст.

---

## 7. Что не реализовано (намеренно, по варианту 1)

- Модель `Skill` и эндпоинты `/projects/skills/`, `/users/skills/` — это варианты 2 и 3.
- Папки `templates_var2/` и `templates_var3/` удалены за ненадобностью.
- Dockerfile для приложения — по ТЗ достаточно держать в Docker только БД, приложение запускается локально через `runserver`.

---

## 8. Чек-лист сдачи

- ✅ PostgreSQL через `docker compose up -d`
- ✅ `requirements.txt` со всеми зависимостями
- ✅ Данные сохраняются в volume `postgres_data`
- ✅ PEP 8 (flake8 без замечаний, `max-line-length = 100`)
- ✅ Тестовые пользователи через `python manage.py seed_demo`
- ✅ Все страницы и переходы по ТЗ работают
- ✅ Автоматические тесты (`pytest`, 36 проходят)
