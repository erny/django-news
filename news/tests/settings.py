DATABASE_ENGINE = 'sqlite3'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'news',
]

ROOT_URLCONF = 'news.tests.urls'

NEWS_BLOCKED_HTML = ['script', 'iframe']
NEWS_NO_HTML_TITLES = True
NEWS_KEY = 'test'
