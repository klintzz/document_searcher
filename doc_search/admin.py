from django.contrib import admin

from doc_search.models import Document

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'done', 'indexed', 'created', 'search_indexed')


admin.site.register(Document, DocumentAdmin)
# admin.site.register(Tag)
# Register your models here.
