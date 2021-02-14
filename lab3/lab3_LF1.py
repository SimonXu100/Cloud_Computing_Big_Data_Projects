import json
import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

def label_rocognize(image):
    rekognition = boto3.client('rekognition', endpoint_url='https://vpce-0a310900e05982757-4gp44wlk.rekognition.us-east-1.vpce.amazonaws.com')
    print(image)
    labels = rekognition.detect_labels(Image=image,MaxLabels=10,MinConfidence=75)
    return [label['Name']  for label in labels['Labels']]
    
def store_photo_to_es(es_instance, s3_image, opt_ts, labels):
    photo_es_object = {
        'objectKey': s3_image['S3Object']['Name'],
        'bucket': s3_image['S3Object']['Bucket'],
        'createdTimestamp': opt_ts, 
        'labels': labels
    }
    es_instance.index(index='photos',doc_type='Photo',id=photo_es_object['objectKey'],body=photo_es_object)

def initial_es(es_instance,index_name):
    index_define_body = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 2
            }
        },
        'mappings': {
            'Photo': {
                'properties': {
                    'objectKey': {'type': 'keyword'},
                    'bucket': {'type': 'text'},
                    'createdTimestamp': {'type': 'date'},
                    'labels': {'type': 'text'}
                }
            }
        }
    }
    es_instance.indices.create(index=index_name, body=index_define_body)
    
def connect_es(host, region):
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
    return es
    
def check_es_photo_index(es_instance, index_name):
    return es_instance.indices.exists(index=index_name)
    
            
def Image_create(bucket_name, image_path):
    return {
        'S3Object': {
            'Bucket': bucket_name,
            'Name': image_path
        }
    }


def lambda_handler(event, context):
    event_time = event['Records'][0]['eventTime']
    s3 = event['Records'][0]['s3']
    bucket_name, image_path = s3['bucket']['name'], s3['object']['key']
    s3_image = Image_create(bucket_name, image_path)
    labels = label_rocognize(s3_image)
    host = 'vpc-photos-nhqs2kwjlmvqiaefek4e5mecnu.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    es_instance = connect_es(host,region)
    if not check_es_photo_index(es_instance,'photos'):
        print('Initialing the \'Photos\' index.')
        initial_es(es_instance,'photos')
    store_photo_to_es(es_instance,s3_image,event_time,labels)
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully put a photo into es.')
    }
