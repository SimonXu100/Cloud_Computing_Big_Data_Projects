from yelp.client import Client
import requests
import json
import boto3
from decimal import Decimal
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

host = 'search-hw-1-dos64yugp3oexuqj3v2xyyhvzy.us-west-2.es.amazonaws.com'
region = 'us-west-2'
service = 'es'
credentials = boto3.Session().get_credentials()
aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=aws_auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
bulk_data = []

index_define_body = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 2
        }
    },
    'mappings': {
        'Restaurant': {
            'properties': {
                'RestaurantID': {'type': 'keyword'},
                'Cuisine': {'type': 'text'},
            }
        }
    }
}
es.indices.create(index='restaurants', body=index_define_body)

api_key = '7wJt3zLoqEVjPOXoQLM6JqKWy4ziIKWuUmPnoW-dA4qEvcYpOweiJAVlzr36IVYKYieOmgh8TSxs90Ff96ll2IJYKV86305U4UXPMQ6ddhQCAgAKjjHTUixopuNGXnYx'
headers = {'Authorization': 'Bearer %s' % api_key}
url = 'https://api.yelp.com/v3/businesses/search'

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('yelp-restaurants')

business_id_set = set()
cuisine_types = ['Seafood', 'Chinese', 'Japanese', 'Burgers', 'Italian', 'Thai', 'Steakhouses']
items = []
for cuisine_type in cuisine_types:
    for offset in range(0, 1000, 50):
        params = {'term': cuisine_type, 'location': 'Manhattan', 'limit': 50, 'offset': offset}
        req = requests.get(url, params=params, headers=headers)
        result = json.loads(req.text)
        restaurants = result['businesses']
        for restaurant in restaurants:
            restaurant_keys = restaurant.keys()
            if 'id' not in restaurant_keys or restaurant['id'] in business_id_set:
                continue
            data_dict = {'RestaurantID': restaurant['id'], 'Cuisine': cuisine_type}
            item = {'Business ID': restaurant['id'], 'Cuisine': cuisine_type, 'insertedAtTimestamp': datetime.now().isoformat()}
            business_id_set.add(restaurant['id'])
            if 'name' in restaurant_keys and restaurant['name']:
                item['Name'] = restaurant['name']
            if 'location' in restaurant_keys and 'display_address' in restaurant['location'].keys() and restaurant['location']['display_address']:
                item['Address'] = ', '.join(restaurant['location']['display_address'])
            if 'coordinates' in restaurant_keys and restaurant['coordinates']:
                item['Coordinates'] = {'latitude': Decimal("%.2f" % restaurant['coordinates']['latitude']),
                                       'longitude': Decimal("%.2f" % restaurant['coordinates']['longitude'])}
            if 'review_count' in restaurant_keys and restaurant['review_count']:
                item['Number of Reviews'] = Decimal(restaurant['review_count'])
            if 'rating' in restaurant_keys and restaurant['rating']:
                item['Number of Reviews'] = Decimal(restaurant['rating'])
            if 'location' in restaurant_keys and 'zip_code' in restaurant['location'].keys() and restaurant['location']['zip_code']:
                item['Zip Code'] = restaurant['location']['zip_code']
            items.append(item)

            op_dict = {
                "index": {
                    "_index": 'restaurants',
                    "_type": 'Restaurant',
                    "_id": data_dict['RestaurantID']
                }
            }
            bulk_data.append(op_dict)
            bulk_data.append(data_dict)

print(len(items))
with table.batch_writer() as batch:
    for item in items:
        batch.put_item(
            Item=item
        )

res = es.bulk(index='restaurants', body=bulk_data)
