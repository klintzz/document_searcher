from django.core.management.base import BaseCommand

from doc_search.models import Document
from haystack.query import SearchQuerySet

from django.utils import timezone

class Command(BaseCommand):

    help = 'mark indexed'

    def handle(self, *args, **options):

        docs = Document.objects.filter(search_indexed=None)

        for doc in docs:
            print doc

            if len(SearchQuerySet().filter(file_name=doc.file_name)) > 0:
                print "marking!"

                doc.search_indexed = timezone.now()

                doc.save()