# MyWishlist

**MyWishlist** — это веб-приложение на Django для создания и управления списками желаний.  
Пользователь может создавать вишлисты, добавлять в них желания, назначать исполнителей, отслеживать статусы выполнения и экспортировать данные.

## Основной функционал

- регистрация и авторизация пользователей;
- личный профиль пользователя;
- создание, редактирование и удаление вишлистов;
- добавление желаний в список;
- указание названия, описания, ссылки, цены и приоритета желания;
- назначение исполнителей по email;
- разграничение доступа между владельцем и исполнителем;
- изменение статуса желания;
- комментарии к желаниям;
- экспорт вишлиста в CSV;
- экспорт вишлиста в PDF;
- административная панель Django;
- автоматические тесты;
- GitHub Actions для проверки проекта.

## Технологии

- Python
- Django
- SQLite
- HTML
- CSS
- GitHub Actions
- ReportLab
- python-dotenv

## Структура проекта

```text
mywishlist/
├── accounts/              # регистрация, авторизация, профиль пользователя
├── wishlists/             # основная логика вишлистов и желаний
├── config/                # настройки Django-проекта
├── templates/             # HTML-шаблоны
├── static/                # CSS и статические файлы
├── .github/workflows/     # GitHub Actions
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Локальный запуск проекта

### 1. Клонировать репозиторий

```bash
git clone https://github.com/a-mar1337/mywishlist.git
cd mywishlist
```

### 2. Создать виртуальное окружение

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать файл `.env`

```bash
cp .env.example .env
```

Для Windows PowerShell:

```powershell
copy .env.example .env
```

Пример содержимого `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
TIME_ZONE=Europe/Warsaw

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### 5. Выполнить миграции

```bash
python manage.py migrate
```

### 6. Создать администратора

```bash
python manage.py createsuperuser
```

### 7. Запустить сервер

```bash
python manage.py runserver
```

После запуска проект будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

Админ-панель:

```text
http://127.0.0.1:8000/admin/
```

## Запуск тестов

```bash
python manage.py test
```

Также тесты автоматически запускаются в GitHub Actions при push и pull request в ветку `main`.

## Переменные окружения

Проект использует файл `.env` для хранения настроек окружения.

Основные переменные:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
TIME_ZONE=Europe/Warsaw

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

Файл `.env` не должен добавляться в GitHub.  
В репозитории хранится только `.env.example`.

## База данных

По умолчанию проект использует SQLite:

```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

Такой вариант удобен для локального запуска и деплоя учебного проекта.

При необходимости проект можно переключить на PostgreSQL, изменив параметры подключения в `.env`.

## Экспорт данных

В проекте реализован экспорт вишлиста:

- в CSV;
- в PDF.

PDF-экспорт реализован с использованием библиотеки ReportLab.

## CI

В проекте настроен GitHub Actions workflow, который:

- устанавливает зависимости;
- запускает миграции;
- выполняет тесты.

Workflow запускается:

- при push в `main`;
- при pull request в `main`;
- вручную через кнопку **Run workflow** во вкладке **Actions**.

## Деплой

Проект подготовлен для деплоя на PythonAnywhere.

Основные шаги деплоя:

1. клонировать репозиторий на PythonAnywhere;
2. создать virtualenv;
3. установить зависимости;
4. создать `.env`;
5. выполнить миграции;
6. собрать static-файлы;
7. настроить WSGI;
8. указать путь к static-файлам;
9. перезагрузить web-приложение.

Подробная инструкция находится в файле:

```text
DEPLOY_PYTHONANYWHERE.md
```

## Авторизация и доступ

В проекте используется кастомная модель пользователя с авторизацией по email.  
Владелец вишлиста может управлять своими списками желаний и назначать исполнителей.  
Исполнитель получает доступ к назначенному вишлисту и может работать с желаниями в рамках предоставленных прав.

## Статус проекта

Проект реализован как учебный Django-проект и демонстрирует:

- работу с моделями и связями между ними;
- формы и представления Django;
- шаблоны;
- авторизацию;
- разграничение доступа;
- работу с файлами экспорта;
- тестирование;
- базовый CI через GitHub Actions;
- подготовку к деплою.
