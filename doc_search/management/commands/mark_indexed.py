from django.core.management.base import BaseCommand

from doc_search.models import Document
from haystack.query import SearchQuerySet
from django.conf import settings
import math

from django.utils import timezone

import logging

logger = logging.getLogger(settings.LOGGER_NAME)

class Command(BaseCommand):

    help = 'mark indexed'

    def handle(self, *args, **options):

        logger.info("$$$$$$ Marking as indexed $$$$$$")

        chunk = 500
        length = Document.objects.filter(indexed=True, search_indexed=None).count()
        pages = int(math.ceil(length / float(chunk)))

        print "total items: %s" % length
        print "total pages: %s" % pages

        logger.info("Total items: %s" % length)
        logger.info("Total pages: %s" % pages)

        for page in xrange(0, pages):
            docs = (Document.objects.filter(indexed=True, search_indexed=None))[0:chunk]

            for doc in docs:

                print doc

                if len(SearchQuerySet().filter(file_name=doc.file_name)) > 0:
                    logger.info("Marking: " + doc.file_name)

                    print "marking!"

                    doc.search_indexed = timezone.now()

                    doc.save()

            print "done processing page %s" % (page + 1)
            logger.info("Done processing page %s" % (page + 1))
