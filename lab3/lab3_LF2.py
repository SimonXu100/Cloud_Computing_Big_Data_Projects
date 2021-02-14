import json
import boto3
import base64
import requests
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection


def lambda_handler(event, context):
    
    query=''
    if 'q' in event['queryStringParameters']:
        query+=event['queryStringParameters']['q']
    
    
    # insert code here:
    # detected search indexes keywords by lex bot
    # query for testing
    # query = 'show me photos with Dog'
    client = boto3.client('lex-runtime')
    userId = 'default'
    response = client.post_text(
        botName='PhotoAlbumQuery',
        botAlias='disambiguation',
        userId=userId,
        inputText=query
    )
    
    keywords = []
    for word in response['slots'].values():
        if word is not None:
            keywords.append(word.capitalize())
    
    # keyword = response['slots']['keyword']
    # ElasticSearch for result
    # searching using url
    
    host = 'https://vpc-photos-nhqs2kwjlmvqiaefek4e5mecnu.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service,
                        session_token=credentials.token)
    
    headers = {"Content-Type": "application/json"}
    index = 'photos'
    
    # create query statement
    
    if(len(keywords) == 1):
        query = {
            "query": {
                "bool": {
                    "must" :[
                        {"match": { "labels": keywords[0]}}
                        ]
                }
            },
            "size": 3
        }
    elif(len(keywords) == 2):
        query = {
        "query": {
            "bool": {
                "must" :[
                    {"match": { "labels": keywords[0]}},
                    {"match": { "labels": keywords[1]}}
                    ]
            }
        },
        "size": 3  # number of rows you want to get in the result
        }
    # method 1
    # search with url searching 
    if(len(keywords) != 0):
        url = host + '/' + index + '/_search'
        print(query)
        res = json.loads(requests.get(url, auth=aws_auth, headers=headers, data=json.dumps(query)).text)
        image_names = [] 
        for hit in res['hits']['hits']:
          image_names.append(hit['_source']['objectKey'])
    
    # method 2:
    '''
    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    res = es.search(index="test-index", body=query)
    image_names = [] 
    for hit in res['hits']['hits']:
      image_names.append(hit['_source']['objectKey'])
    
    return {
        'statusCode': 200,
        'body': str(image_names)
    }
    '''
    
    rets=[]
    for name in image_names:
        client=boto3.client('s3')
        response = client.get_object(
            Bucket='hw3-ai-photo-album',
            Key=name
        )
        
        img=response['Body'].read()
        b64=base64.b64encode(img).decode()
        prefix='data:image/{};base64,'.format(name.split('.')[-1])
        ret=prefix+b64
        rets.append(ret)
    
    return {
        "isBase64Encoded": False,
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": '*' ,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': str(rets)
    }
    