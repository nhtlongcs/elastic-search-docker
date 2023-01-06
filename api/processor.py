import json
import pprint
from elasticsearch import Elasticsearch, RequestsHttpConnection
from query_generator import QueryGenerator
from query_analyser import QueryAnalyser
from utils import time_this

class Processor:
    def __init__(self, config):
        self.host = config.ES_HOST
        self.port = config.ES_PORT
        self.index = config.ES_INDEX
        self.return_size = config.ES_RETURN_SIZE
        self.es = self._connect()
        self.generator = QueryGenerator(self.es, config)
        self.analyser = QueryAnalyser(self.generator)

    def _connect(self):
        es = Elasticsearch(['http://0.0.0.0:9200'], connection_class=RequestsHttpConnection, http_auth=('elastic', '123456'), use_ssl=False, verify_certs=False)

        # es = Elasticsearch([{'host':self.host, 'port':self.port}])
        if es.ping():
            print("Connected to Elasticsearch node")
        else:
            print("Error: Cannot connect to Elasticsearch cluster")
        return es


    def update_data_field(self, doc_id, field, value):
        body = {
            "script": "ctx._source.{0} = {1}".format(field, value)
        }
        result = self.es.update(index=self.index, id=doc_id, body=body)
        return result


    """
    Main function for searching in elasticsearch
    """
    @time_this
    def search(self, text_query, incremental_query=False, document_set=None):
        self.generator.reset_query()
        should_type_query = True
        if incremental_query:
            self.generator.add_document_set(document_set)
            should_type_query = False
        self.analyser.analyse(text_query, optional=should_type_query)
        query = self.generator.run(profiler=False)
        print(query)
        result = self.es.search(index=self.index, body=json.dumps(query), size=self.return_size)
        #print(result['profile']['shards'][0]['searches'][0]['query'][0]['description'])
        #logger.log(result['profile']['shards'][0]['searches'][0]['query'][0]['description'])
        return result

    @time_this
    def get_document_by_id(self, ids):
        query = {
            "query": {
                "ids" : {
                    "values" : ids
                }
            }
        }
        result = self.es.search(query, size=self.return_size)
        return result['hits']['hits']

