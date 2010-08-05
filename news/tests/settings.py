DATABASE_ENGINE = 'sqlite3'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'news',
]

ROOT_URLCONF = 'news.tests.urls'

NEWS_BLOCKED_HTML = ['script', 'iframe']
