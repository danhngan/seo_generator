import os
from big_seo.crawler.core import WebPage
from big_seo.storage.mongo_constants import DEFAULT_DB, DEFAULT_WEB_PAGES_COLLECTION


from mongoengine import (connect,
                         Document,
                         EmbeddedDocument,
                         fields)


def connect_db(db=DEFAULT_DB, alias=DEFAULT_DB,
               host='localhost', port=2717,
               username=os.getenv('MONGO_USERNAME'),
               password=os.getenv('MONGO_PASSWORD'),
               authentication_source='admin'
               ):
    connect(db=db, host=host, port=port,
            username=username,
            password=password,
            authentication_source=authentication_source,
            alias=alias)


class WebPageMongo(Document, WebPage):
    page_id = fields.BinaryField(primary_key=True)
    url = fields.StringField()
    domain = fields.StringField()
    title = fields.StringField()
    ingestion_time = fields.DateTimeField()
    full_content = fields.StringField()
    headings = fields.StringField()
    main_content = fields.StringField()
    keywords = fields.ListField(fields.StringField())
    rank = fields.IntField()

    meta = {
        'db_alias': DEFAULT_DB,
        'indexes': [
            'url',
            'domain',
            'title',
            'ingestion_time',
            'keywords',
            'rank'
        ],
    }


########
# IndexMapper
########

# class MongoIndexMapper(Document, IIndexMapper):
#     vec = fields.ListField(fields.FloatField())
#     doc_id = fields.BinaryField()

#     meta = {
#         'db_alias': DEFAULT_DB,
#         'indexes': [
#             'doc_id'
#         ],
#     }
