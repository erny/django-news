from django.test import TestCase

from news.models import Feed, Article, Category, WhiteListFilter


class FakeFeed(object):
    encoding = 'utf-8'
    
    def __init__(self):
        self.entries = []

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
            {'title': 'Hg rules and its python', 'summary': '<p>trolled</p>', 'link': '/hg/'},
            {'title': 'Django stuff', 'summary': '', 'link': '/django/'},
            {'title': 'Python and Django rock', 'summary': '<p>Programming article about python and django</p>', 'link': '/p+d+rokk/'},
        ],
        'Geek': [
            {'title': 'Apple <b>gear</b>', 'summary': '<script>/* hax0r3d */</script>I <3 apple', 'link': '/apple/'},
            {'title': 'Homemade wallets', 'description': 'In forty three <b>easy</b> steps <iframe src="somesuch" />', 'link': '/wtf/'},
        ],
        'Hacker News RSS': [
            {'title': 'Being a startup', 'summary': 'damn hard', 'link': '/momoney/'},
            {'title': 'VC Angels', 'summary': 'where dey', 'link': '/whodat/'},
            {'title': 'A python article', 'summary': 'awesome', 'link': '/python/'},
            {'title': 'A django article', 'summary': 'awesome', 'link': '/django/'},
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
        # basically this test just makes sure that when given some comma
        # separated keywords we can parse them into a nice list
        test_whitelist = WhiteListFilter(name='Test', keywords='test1, test2')
        self.assertEqual(test_whitelist.get_keyword_list(), ['test1', 'test2'])
        
        test_whitelist.keywords = 'test1, test2, ,'
        self.assertEqual(test_whitelist.get_keyword_list(), ['test1', 'test2'])
    
        test_whitelist.keywords = 'test1 test2'
        self.assertEqual(test_whitelist.get_keyword_list(), ['test1 test2'])
    
    def test_category_path_updating(self):
        # if a top level category is saved, since the url path is cached on
        # the model, it needs to be updated on all descendents.
        programming = Category.objects.get(name='Programming')
        programming.name = 'Progging'
        programming.slug = 'progging'
        programming.save()
        
        # check that python's url path changed from /programming/ to /progging/
        python = Category.objects.get(name='Python')
        self.assertEqual(python.url_path, 'progging/python/')
        
        django = Category.objects.get(name='Django')
        self.assertEqual(django.url_path, 'progging/python/django/')
    
    def test_item_sanitization(self):
        feed = Feed.objects.get(name='Geek')
        feed_data = feed.fetch_feed()
        apple, wallet = feed_data.entries
        
        # apple article had some innocuous HTML in the title, but lets the
        # settings are configured to remove it, so do it.  also remove the
        # script tags within the summary
        apple_article = feed.sanitize_item(apple)
        self.assertEqual(apple_article.headline, 'Apple gear')
        self.assertEqual(apple_article.content, 'I <3 apple')
        self.assertEqual(apple_article.url, '/apple/')
        self.assertEqual(apple_article.guid, '/apple/')
        
        # here just making sure that the html blacklist will kill the iframe
        # tag while leaving the bold tags intact
        wallet_article = feed.sanitize_item(wallet)
        self.assertEqual(wallet_article.headline, 'Homemade wallets')
        self.assertEqual(wallet_article.content, 'In forty three <b>easy</b> steps ')
        self.assertEqual(wallet_article.url, '/wtf/')
        self.assertEqual(wallet_article.guid, '/wtf/')
    
    def test_categorization_simple(self):
        geek = Category.objects.get(name='Geek')
        
        # grab the two articles from this feed
        feed = Feed.objects.get(name='Geek')
        feed_data = feed.fetch_feed()
        apple, wallet = feed_data.entries
        
        # sanitize the feed data to get an unsaved article instance and
        # see that it gets categorized properly
        apple_article = feed.sanitize_item(apple)
        apple_categories = feed.get_categories_for_article(apple_article)
        
        self.assertEqual(apple_categories, [geek])
        
        wallet_article = feed.sanitize_item(wallet)
        wallet_categories = feed.get_categories_for_article(wallet_article)
        
        self.assertEqual(wallet_categories, [geek])
    
    def test_subcategorization(self):
        # grab the categories from the database
        programming = Category.objects.get(name='Programming')
        python = Category.objects.get(name='Python')
        django = Category.objects.get(name='Django')
        
        # the programming feed is interesting from a testing perspective b/c
        # it contains a subcategory that autopopulates from it, and that
        # subcategory has a subcategory in turn.
        #
        # Programming -> Python -> Django  --  a whitelist is applied to the
        # articles, so non python articles won't make it from Programming to
        # Python.
        #
        # NOTE: that an article will follow all descendent relations, so an
        # article in Programming can skip the Python category but make it into
        # the Django category if it passes the whitelist between Py & Django
        feed = Feed.objects.get(name='Programming')
        feed_data = feed.fetch_feed()
        
        git, hg, dj, py = feed_data.entries
        
        # this article will go into the programming category directly, but
        # it will not propagate to any descendent categories
        git_article = feed.sanitize_item(git)
        git_categories = feed.get_categories_for_article(git_article)
        
        self.assertEqual(git_categories, [programming])
        
        # this article will also go into the python category because it
        # has the word "python" in the headline
        hg_article = feed.sanitize_item(hg)
        hg_categories = feed.get_categories_for_article(hg_article)
        
        self.assertEqual(hg_categories, [programming, python])
        
        # this article will go into the django category, skipping the python
        # one altogether
        dj_article = feed.sanitize_item(dj)
        dj_categories = feed.get_categories_for_article(dj_article)
        
        self.assertEqual(dj_categories, [programming, django])
        
        # this article will go into all three as it has 'python' and 'django'
        # in the headline
        py_article = feed.sanitize_item(py)
        py_categories = feed.get_categories_for_article(py_article)
        
        self.assertEqual(py_categories, [programming, python, django])
    
    def test_whitelisting(self):
        # grab the categories
        programming = Category.objects.get(name='Programming')
        python = Category.objects.get(name='Python')
        django = Category.objects.get(name='Django')
        geek = Category.objects.get(name='Geek')
        
        # hacker news will go into programming if it matches python or django,
        # otherwise it just goes to geek
        feed = Feed.objects.get(name='Hacker News RSS')
        feed_data = feed.fetch_feed()
        
        misc, misc, py, dj = feed_data.entries
        
        misc_article = feed.sanitize_item(misc)
        misc_categories = feed.get_categories_for_article(misc_article)
        
        self.assertEqual(misc_categories, [geek])
        
        py_article = feed.sanitize_item(py)
        py_categories = feed.get_categories_for_article(py_article)
        
        self.assertEqual(py_categories, [geek, programming, python])
        
        # once again, the article passes the whitelist filter between the
        # hacker news -> programming category, then once in the programming
        # it will propagate down to the django category
        dj_article = feed.sanitize_item(dj)
        dj_categories = feed.get_categories_for_article(dj_article)
        
        self.assertEqual(dj_categories, [geek, programming, django])
    
    def test_feed_repeatability(self):
        # feed fetching needs to be repeatable so it can get cron'd up, lets
        # test that
        feed = Feed.objects.get(name='Programming')
        results = feed.process_feed()
        self.assertEqual(results, 4)
        
        results = feed.process_feed()
        self.assertEqual(results, 0)
    
    def test_feed_processing(self):
        # double check that the articles are categorized properly even though
        # the underlying methods are covered elsewhere in the tests
        feed = Feed.objects.get(name='Programming')
        results = feed.process_feed()
        
        self.assertEqual(Article.objects.all().count(), 4)
        
        # load everything up from the db
        git = Article.objects.get(headline='Git rules')
        hg = Article.objects.get(headline='Hg rules and its python')
        dj = Article.objects.get(headline='Django stuff')
        py = Article.objects.get(headline='Python and Django rock')
        
        programming = Category.objects.get(name='Programming')
        python = Category.objects.get(name='Python')
        django = Category.objects.get(name='Django')
        
        self.assertEqual(list(git.categories.all()), [programming])
        self.assertEqual(list(hg.categories.all()), [programming, python])
        self.assertEqual(list(dj.categories.all()), [programming, django])
        self.assertEqual(list(py.categories.all()), [programming, python, django])
