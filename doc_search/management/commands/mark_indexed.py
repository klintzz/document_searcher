from django.core.management.base import BaseCommand

from doc_search.models import Document
from haystack.query import SearchQuerySet
from django.core.paginator import Paginator

from django.utils import timezone

class Command(BaseCommand):

    help = 'mark indexed'

    def handle(self, *args, **options):

        paginator = Paginator( Document.objects.filter(indexed=True, search_indexed=None), 500)

        for page in range(1, paginator.num_pages):
            for doc in paginator.page(page).object_list:

                print doc

                if len(SearchQuerySet().filter(file_name=doc.file_name)) > 0:
                    print "marking!"

                    doc.search_indexed = timezone.now()

                    doc.save()

            print "done processing page %s" % page
