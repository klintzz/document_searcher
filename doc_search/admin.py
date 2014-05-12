from django.contrib import admin

from doc_search.models import Document, Tag

admin.site.register(Document)
admin.site.register(Tag)
# Register your models here.
