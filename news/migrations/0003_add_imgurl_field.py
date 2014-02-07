
from south.db import db
from django.db import models
from news.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Article.imgurl'
        db.add_column('news_article', 'imgurl', orm['news.article:imgurl'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Article.imgurl'
        db.delete_column('news_article', 'imgurl')
        
    
    
    models = {
        'news.article': {
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.Category']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expired': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'articles'", 'to': "orm['news.Feed']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imgurl': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'publish': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'news.category': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.Category']", 'symmetrical': 'False'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'children'", 'null': 'True', 'blank': 'True', 'to': "orm['news.Category']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'url_path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'news.categoryrelationship': {
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': "orm['news.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included_category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'included_categories'", 'to': "orm['news.Category']"}),
            'white_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.WhiteListFilter']", 'blank': 'True'})
        },
        'news.feed': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.Category']"}),
            'fetch_all_articles': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_download': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'new_articles_added': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news.Source']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'news.feedcategoryrelationship': {
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news.Category']"}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news.Feed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'white_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.WhiteListFilter']", 'blank': 'True'})
        },
        'news.source': {
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'news.whitelistfilter': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['news']
