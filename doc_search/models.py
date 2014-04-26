from django.db import models

class Tag(models.Model):
    def __unicode__(self):
        return self.text

    text = models.CharField(max_length=200, unique=True, db_index=True)

class Document(models.Model):
    def __unicode__(self):
        return self.file_name

    file_name = models.CharField(max_length=32, unique=True, db_index=True)
    # document_text = models.TextField()
    tags = models.ManyToManyField(Tag)
    done = models.BooleanField(default=False)
    indexed = models.BooleanField(default=False)