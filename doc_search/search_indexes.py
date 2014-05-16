from haystack import indexes
from doc_search.models import Document

class DocumentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # tags = indexes.CharField(model_attr='tags', null=True)
    # document_text = indexes.CharField(model_attr='document_text')

    def get_model(self):
        return Document

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(indexed=True)

    # def prepare_tags(self, obj):
    #     return [tag.text for tag in obj.tags.all()]
