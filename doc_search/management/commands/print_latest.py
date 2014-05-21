from django.core.management.base import BaseCommand

from doc_search.models import Document

class Command(BaseCommand):

    help = 'print latest'

    def handle(self, *args, **options):
        print Document.objects.latest('id').id