import json 
from elasticsearch import Elasticsearch
from utils import time_this
import json 
import logging
class QueryGenerator:
    def __init__(self, es, config): 
        self.es = es

        self.INDEX_FIELDS = []
        self.MUST = []
        self.SHOULD = []
        self.FILTER = []
        self.DOCUMENT_IDS = []

        if self.es.ping():
            mapping = self.es.indices.get_mapping(config.ES_INDEX)
            fields = mapping[config.ES_INDEX]['mappings']['properties']
            for field in fields:
                if fields[field].get('type', None) == 'text':
                    self.INDEX_FIELDS.append(field)


    def gen_multi_matching_query(self, fields, values, optional=True, auto_fill=False):
        if auto_fill:
            weighted_fields = ["{0}^{1}".format(x, fields[x]) if x in fields else x for x in self.INDEX_FIELDS]
        else:
            weighted_fields = ["{0}^{1}".format(x, fields[x]) for x in fields]

        pattern = {"multi_match": {
            "query": values, 
            "fields": weighted_fields,
            "type": "most_fields" }}
        if optional:
            self.SHOULD.append(pattern)
        else: 
            self.MUST.append(pattern)


    def gen_matching_query(self, field, values, optional=True):
        pattern = {"match": {field: values}}
        if optional:
            self.SHOULD.append(pattern)
        else: 
            self.MUST.append(pattern)

    def gen_query_string_query(self, fields, values, optional=True):
        logging.debug('fields', fields)
        pattern = {
            "query_string": {
                "query": values,
                "fields": fields,
                "type": "most_fields",
                "default_operator": "OR"
            }
        }

        if optional: 
            self.SHOULD.append(pattern)
        else:
            self.MUST.append(pattern)


    def gen_term_query(self, field, values, is_filter=True):
        pattern = {"term": {field: values}}
        if is_filter: 
            self.FILTER.append(pattern)
        else:
            self.MUST.append(pattern)


    def gen_range_query(self, field, value_from, value_to, value_format, is_filter=True): 
        pattern = {
            "range": {
                field: {
                    "gte": value_from,
                    "lte": value_to,
                    "format": value_format
                }     
            }
        } 
        if is_filter: 
            self.FILTER.append(pattern)
        else:
            self.MUST.append(pattern)


    def gen_match_all_query(self):
        pattern = {"match_all": {}}
        self.SHOULD.append(pattern)


    def reset_query(self):
        self.INDEX_FIELDS = []
        self.MUST = []
        self.SHOULD = []
        self.FILTER = []
        self.DOCUMENT_IDS = []

    def add_document_set(self, document_set):
        self.DOCUMENT_IDS = document_set
        self.MUST.append({
            "ids": {
                "values": self.DOCUMENT_IDS
            }
        })


    @time_this
    def run(self, profiler=False):
        query = {}
        bool_query = {}
        if len(self.MUST) > 0:
            bool_query["must"] = self.MUST
        if len(self.SHOULD) > 0:
            bool_query["should"] = self.SHOULD
        if len(self.FILTER) > 0:
            bool_query["filter"] = self.FILTER
        query["query"] = {"bool": bool_query}

        if profiler:
            query["profile"] = False
        return query


