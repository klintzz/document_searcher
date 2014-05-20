from django.core.management.base import BaseCommand

from doc_search.models import Document
from haystack.query import SearchQuerySet
import math

from django.utils import timezone

class Command(BaseCommand):

    help = 'mark indexed'

    def handle(self, *args, **options):

        chunk = 50.
        length = len(Document.objects.filter(indexed=True, search_indexed=None))
        pages = math.ceil(length / chunk)

        print "total items: %s" % length
        print "total pages: %s" % pages

        for page in xrange(0, pages - 1):
            docs = (Document.objects.filter(indexed=True, search_indexed=None))[0:chunk]

            for doc in docs:

                print doc

                if len(SearchQuerySet().filter(file_name=doc.file_name)) > 0:
                    print "marking!"

                    doc.search_indexed = timezone.now()

                    doc.save()

            print "done processing page %s" % (page + 1)
