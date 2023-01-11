from blog.models import Post

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, tokenizer


@registry.register_document
class PostDocument(Document):
    autocomplete_analyzer = analyzer(
        'autocomplete_analyzer', tokenizer=tokenizer('trigram', 'nGram', min_gram=1, max_gram=20), filter=['lowercase']
    )

    title = fields.TextField(required=True, analyzer=autocomplete_analyzer)
    # title = fields.TextField(
    #     analyzer=autocomplete_analyzer,
    #     fields={
    #         'raw': fields.TextField(analyzer=autocomplete_analyzer),
    #     },
    # )

    class Index:
        name = 'posts'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0, 'max_ngram_diff': 20}

    class Django:
        model = Post

        fields = [
            'text',
            'date_created',
        ]
