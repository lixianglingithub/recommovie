from db.data_opt import DataOperation
from elasticsearch import Elasticsearch, helpers, exceptions
from util import Util

util = Util()
db = DataOperation()

config = util.get_params()
es = Elasticsearch(hosts=[{'host': config['elastic']['host'], 'port': config['elastic']['port']}])


class Elastic:
    @staticmethod
    def insert_elastic():
        """
        Insert records to elasticsearch

        :return: difference between inserted and sent
        :rtype: int
        """
        items = db.get_items()

        actions = []

        for item in items:
            action = {
                '_index': f"{config['elastic']['index']}",
                '_type': f"{config['elastic']['type']}",
                '_id': item[0],
                '_source': {
                    'name': item[1],
                    'year': item[2],
                },
            }
            actions.append(action)

        response = helpers.bulk(es, actions)
        return len(items) - response[0]

    @staticmethod
    def create_index():
        """
        Create index in elasticsearch

        :return: status of request
        :rtype: bool
        """
        request_body = {
            'setting': {
                'number_of_shards': 3,
                'number_of_replicas': 1,
            },
            'mappings': {
                'movies': {
                    'properties': {
                        'name': {
                            'type': 'completion',
                            'preserve_separators': False,
                            'preserve_position_increments': False,
                        },
                        'year': {
                            'type': 'keyword',
                        }
                    }
                }
            }
        }
        message = None

        try:
            es.indices.create(index=config['elastic']['index'], body=request_body)
        except exceptions.RequestError as e:
            if not e.args[1] == 'resource_already_exists_exception':
                message = e.args
        finally:
            return message
