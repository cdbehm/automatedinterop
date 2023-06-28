# import libraries
from datetime import datetime , timedelta
from elasticsearch import Elasticsearch
from elasticsearch.connection import create_ssl_context
import ssl


class WebServicesELK:
    es_url = 'https://abe-elk-shs-data-es.oss.telus.com:443/'
    es_api_key = ('2-RJ03kBYaMiFoi4cLoB' , 'S9U-OLW3RQ-5F-XjLIcxFg')
    ssl_context = create_ssl_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    es_client = None
    search_query = None

    def __init__(self):
        self.es_client = Elasticsearch([self.es_url] , api_key=self.es_api_key , timeout=60 , http_compress=True , scheme='https' , ssl_context=self.ssl_context)

    def build_search_query(self , search_date , model , dealer_id):
        self.search_query = {
            "version": True ,
            "size": 10000 ,
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc" ,
                        "unmapped_type": "boolean"
                    }
                }
            ] ,
            "stored_fields": [
                "*"
            ] ,
            "docvalue_fields": [
                {
                    "field": "@timestamp" ,
                    "format": "date_time"
                } ,
                {
                    "field": "customer_termination_date" ,
                    "format": "date_time"
                } ,
                {
                    "field": "device_install_date" ,
                    "format": "date_time"
                } ,
                {
                    "field": "device_removal_date" ,
                    "format": "date_time"
                } ,
                {
                    "field": "last_update" ,
                    "format": "date_time"
                } ,
                {
                    "field": "unknown_date" ,
                    "format": "date_time"
                }
            ] ,
            "_source": {
                "excludes": []
            } ,
            "query": {
                "bool": {
                    "must": [] ,
                    "filter": [
                        {
                            "match_all": {}
                        } ,
                        {
                            "bool": {
                                "should": [
                                    {
                                        "match_phrase": {
                                            "device_model_name": model
                                        }
                                    }
                                ] ,
                                "minimum_should_match": 1
                            }
                        } ,
                        {
                            "match_phrase": {
                                "holding_dealer_organic_id": dealer_id
                            }
                        } ,
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": "2005-01-23T01:00:00.000Z" ,
                                    "lte": search_date + "T00:00:00.000Z" ,
                                    "format": "strict_date_optional_time"
                                }
                            }
                        }
                    ] ,
                    "should": [] ,
                    "must_not": [
                        {
                            "exists": {
                                "field": "device_removal_date"
                            }
                        } ,
                        {
                            "exists": {
                                "field": "customer_termination_date"
                            }
                        }
                    ]
                }
            }
        }

    def get_devices(self , model , dealer_id , field=None):
        self.build_search_query(datetime.today().strftime("%Y-%m-%d") , model , dealer_id)
        print(self.search_query)

        inventory_lists = []
        es_response = self.es_client.search(index='inventory-*' , body=self.search_query , scroll='1m')
        inventory_lists.append(es_response['hits']['hits'])
        scroll_id = es_response['_scroll_id']
        scroll_hits = {"": ""}
        while len(scroll_hits) != 0:
            es_scroll_response = self.es_client.scroll(scroll_id=scroll_id , scroll='1m')
            scroll_hits = es_scroll_response['hits']['hits']
            inventory_lists.append(scroll_hits)
            scroll_id = es_scroll_response['_scroll_id']
        output = []
        for inventory_list in inventory_lists:
            for device in inventory_list:
                if not field:
                    output.append(str(device['_source']['customer_id']) + "," + str(device['_source']['device_organic_id']))
                else:
                    output.append(str(device['_source'][field]))
        return output

    def get_most_recent_devices(self , model , dealer_id):
        hits = {}
        doorbells = []
        days_to_subtract = 0
        while len(hits) == 0:
            self.build_search_query((datetime.today() - timedelta(days=days_to_subtract + 1)).strftime("%Y-%m-%d") , model , dealer_id)
            es_response = self.es_client.search(index='inventory-*' , body=self.search_query , scroll='1m')
            hits = es_response['hits']['hits']
            if len(hits) != 0:
                scroll_id = es_response['_scroll_id']
                doorbells.append(hits)
                scroll_hits = {"": ""}
                while len(scroll_hits) != 0:
                    es_scroll_response = self.es_client.scroll(scroll_id=scroll_id , scroll='1m')
                    scroll_hits = es_scroll_response['hits']['hits']
                    doorbells.append(scroll_hits)
                    scroll_id = es_scroll_response['_scroll_id']
                break
            days_to_subtract += 1
        output = []
        for doorbell in doorbells:
            for device in doorbell:
                output.append(str(device['_source']['customer_id']) + "," + str(device['_source']['device_organic_id']))
        return output