import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-gift-study-project"
DEBUG = True
ALLOWED_HOSTS: list[str] = []

# Признак запуска автотестов: Debug Toolbar в тестах не подключается.
TESTING = "test" in sys.argv or "pytest" in sys.modules

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "gift_web.apps.GiftWebConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Django Debug Toolbar - только при разработке (DEBUG) и не в тестах.
if DEBUG and not TESTING:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]
    # Панель свёрнута, пока её не откроют кнопкой «DjDT» справа.
    DEBUG_TOOLBAR_CONFIG = {"SHOW_COLLAPSED": True}

ROOT_URLCONF = "gift_project.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "gift_web" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "gift_web.context_processors.site_context",
            ],
        },
    }
]
WSGI_APPLICATION = "gift_project.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = []
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "gift_web" / "static"]

# Загруженные пользователями файлы (фото подарков) хранятся отдельно
# от статических файлов приложения.
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Количество подарков на одной странице списка.
GIFTS_PER_PAGE = 3
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
