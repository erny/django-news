from django.test import TestCase

class NewsModelsTestCase(TestCase):
    fixtures = ['news_test_data']
    urls = 'news.tests.urls'
