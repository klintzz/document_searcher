from django.core.management.base import BaseCommand
from doc_search.models import Document
from django.conf import settings

import urllib
import time
import random
import os
import shutil
import logging

logger = logging.getLogger(settings.LOGGER_NAME)


def get_url(id):
    return "http://www.adviserinfo.sec.gov/Iapd/Content/Common/crd_iapd_Brochure.aspx?BRCHR_VRSN_ID={0}".format(id)

class Command(BaseCommand):
    help = 'parse files into tags'

    def handle(self, *args, **options):
        logger.info('&&&&&&& Pulling new docs! &&&&&&')

        start_id = Document.objects.latest('id').id + 1


        for i in xrange(start_id, start_id + settings.NEW_FILE_INCREMENT):
            url = get_url(i)

            tmpfilename = "{0}.pdf".format(i)

            print tmpfilename
            logger.info(tmpfilename)

            urllib.urlretrieve(url, tmpfilename)

            f = open(tmpfilename, "rb")
            start = f.read(50)
            f.close()

            if ("No data found" in start):
                print "Fail\n"
                logger.info("Fail")
                os.remove(tmpfilename)
            else:
                if(os.path.isfile(os.path.join(settings.ROOT_NEW_DIR, tmpfilename))):
                    os.remove(tmpfilename)
                    print("Exists\n")
                    logger.info("Exists")
                else:
                    shutil.move(tmpfilename, settings.ROOT_NEW_DIR)
                    print("Moving\n")
                    logger.info("Moving")

            time.sleep(random.random() + .5)