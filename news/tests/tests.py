from django.test import TestCase

from news.models import Feed, Article, Category, WhiteListFilter


class FakeFeed(object):
    encoding = 'utf-8'
    entries = []

class FakeFeedItem(dict):
    def __getattr__(self, attr):
        if self.__contains__(attr):
            return self[attr]
        raise AttributeError


class NewsModelsTestCase(TestCase):
    fixtures = ['news_test_data']
    urls = 'news.tests.urls'
    
    fake_feed_data = {
        'Django': [
            {'title': 'Django #1', 'summary': '<p>Article 1 about django</p>', 'link': '/d1/'},
            {'title': 'Django #2', 'summary': '<p>Article 2 about django</p>', 'link': '/d2/'},
            {'title': 'Django + Python #1', 'summary': '<p>Article 1 about django and python</p>', 'link': '/d+p/'},
        ],
        'Python': [
            {'title': 'Python #1', 'summary': '<p>Article 1 about python</p>', 'link': '/p1/'},
            {'title': 'Python #2', 'summary': '<p>Article 2 about python</p>', 'link': '/p2/'},
            {'title': 'Python + Django #1', 'summary': '<p>Article 1 about python and django</p>', 'link': '/p+d/'},
        ],
        'Programming': [
            {'title': 'Git rules', 'summary': '<p>vcs troll</p>', 'link': '/git/'},
            {'title': 'Hg rules', 'summary': '<p>trolled</p>', 'link': '/hg/'},
            {'title': 'Python and Django rock', 'summary': '<p>Programming article about python and django</p>', 'link': '/p+d+rokk/'},
        ],
        'Geek': [
            {'title': 'Apple <b>gear</b>', 'summary': '<script>/* hax0r3d */</script>I <3 apple', 'link': '/apple/'},
            {'title': 'Homemade wallets', 'description': 'In forty three <b>easy</b> steps <iframe src="somesuch" />', 'link': '/wtf/'},
        ],
        'Hacker News RSS': [
            {'title': 'Being a startup', 'summary': 'damn hard', 'link': '/momoney/'},
            {'title': 'VC Angels', 'summary': 'where dey', 'link': '/whodat/'},
        ]
    }
    
    def get_feed(self, key):
        ff = FakeFeed()
        for item in self.fake_feed_data[key]:
            ff.entries.append(FakeFeedItem(item))
        return ff
    
    def setUp(self):
        #   /~\
        #  C oo
        #  _( ^)
        # /   ~\
        self.orig_fetch_feed = Feed.fetch_feed
        Feed.fetch_feed = lambda f: self.get_feed(f.name)
    
    def tearDown(self):
        Feed.fetch_feed = self.orig_fetch_feed

    def test_keyword_list(self):
        test_whitelist = WhiteListFilter(name='Test', keywords='test1, test2')
        self.assertEqual(test_whitelist.get_keyword_list(), ['test1', 'test2'])
        
        test_whitelist.keywords = 'test1, test2, ,'
        self.assertEqual(test_whitelist.get_keyword_list(), ['test1', 'test2'])
    
        test_whitelist.keywords = 'test1 test2'
        self.assertEqual(test_whitelist.get_keyword_list(), ['test1 test2'])
    
    def test_category_path_updating(self):
        programming = Category.objects.get(name='Programming')
        programming.name = 'Progging'
        programming.slug = 'progging'
        programming.save()
        
        python = Category.objects.get(name='Python')
        self.assertEqual(python.url_path, 'progging/python/')
        
        django = Category.objects.get(name='Django')
        self.assertEqual(django.url_path, 'progging/python/django/')
    
    def test_item_sanitization(self):
        feed = Feed.objects.get(name='Geek')
        feed_data = feed.fetch_feed()
        apple, wallet = feed_data.entries
        
        apple_article = feed.sanitize_item(apple)
        self.assertEqual(apple_article.headline, 'Apple gear')
        self.assertEqual(apple_article.content, 'I <3 apple')
        self.assertEqual(apple_article.url, '/apple/')
        self.assertEqual(apple_article.guid, '/apple/')
        
        wallet_article = feed.sanitize_item(wallet)
        self.assertEqual(wallet_article.headline, 'Homemade wallets')
        self.assertEqual(wallet_article.content, 'In forty three <b>easy</b> steps ')
        self.assertEqual(wallet_article.url, '/wtf/')
        self.assertEqual(wallet_article.guid, '/wtf/')
