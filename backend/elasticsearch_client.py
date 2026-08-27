import os

from elasticsearch import AsyncElasticsearch


ELASTICSEARCH_URL = os.getenv(
    "ELASTICSEARCH_URL",
    "http://localhost:9200",
)

es = AsyncElasticsearch(
    ELASTICSEARCH_URL,
)