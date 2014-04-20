from django.core.management.base import BaseCommand
from doc_search.models import Document, Tag

import os
import subprocess
import re
import gc

STOP_WORDS = set(["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"])
STOP_WORDS.update(["page", "pages", "yes"])

class Command(BaseCommand):
    args = '<folder location>'
    help = 'parse files into tags'

    def handle(self, *args, **options):
        rootdir = '/home/ec2-user/files'

        files_in_dir = os.listdir(rootdir)

        for file_in_dir in files_in_dir:
            if file_in_dir.endswith(".pdf"):

                document_id = re.sub('[^0-9]+', '', file_in_dir)

                document, created = Document.objects.get_or_create(file_name=file_in_dir, id=document_id)

                print document

                if document.done:
                    continue

                # pages = subprocess.check_output(["pdftotext", os.path.join(rootdir, file_in_dir), "-"])
                os.system('pdftotext ' + os.path.join(rootdir, file_in_dir))
                f = open(os.path.join(rootdir, document_id+'.txt'), 'r')
                pages = f.read()
                f.close()
                # textSet = set()

                for word in pages.split():
                    processed = re.sub('[^0-9a-zA-Z]+', '', word).lower()

                    if len(processed) > 2 and processed not in STOP_WORDS and not processed.isdigit():
                        # textSet.add(processed)

                        tag, created = Tag.objects.get_or_create(text=processed)

                        document.tags.add(tag)


                #document.document_text = ' '.join([x for x in textSet])
                document.done = True
                document.save()
		gc.collect()
