# python 3.7
import boto3
import requests
from requests_aws4auth import AWS4Auth
import json
#from botocore.vendored import Elasticsearch, RequestsHttpConnection, helpers
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    # Pick message from SQS
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='Q1')
    #cuisines = queue.receive_messages(MessageAttributeNames=['cuisine'])
    
    preference_info = queue.receive_messages(MessageAttributeNames=["All"])
    cuisine_name = ""

    
    for info in preference_info:
        # Get the custom author message attribute if it was set
        if info.message_attributes is not None:
            cuisine_name = info.message_attributes.get('cuisine').get('StringValue')
            
            # Elastic search
            if cuisine_name:
                final_response = []
                dynamoDB_search_keys = recommend_search(cuisine_name)
                
                for dynamoDB_search_key in dynamoDB_search_keys:
                    
                    final_response.append(dynamoDB_search(dynamoDB_search_key).get("Items")[0])

                # format the response
                phone_number = info.message_attributes.get('phone_number').get('StringValue')
                people_number = info.message_attributes.get('people_number').get('StringValue')
                dining_time = info.message_attributes.get('dining_time').get('StringValue')
                sms_message = "Hello! Here are my {0} restaurant suggestions for {1}people, for today at {2}: ".format(cuisine_name, people_number, dining_time)
                i = 1
                
                for restaurant in final_response:
                    temp_string = "{0}. {1}, located at {2}".format(i, restaurant['Name'] ,restaurant['Address'])
                    if i <= len(final_response):
                        temp_string += ", "
                    else:
                        break
                    sms_message = sms_message + temp_string
                    i = i + 1

                sms_message += ". Enjoy your meal!"
                
                

                # could develop recommend poly: such as firstly recommend restaurant with high rating
                # send message
                send_sms(sms_message, phone_number)
                #response_sms = send_sms(sms_message, "+16467145790")
                
                info.delete()
                
    return {
        'statusCode': 200,
        'body': "the message has been sent"
    } 
                
    
    
def recommend_search(cuisine_key):
    host = 'https://search-hw1-f3oyhvtn4ldleqapywpa72zd54.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service,
                        session_token=credentials.token)
    
    headers = {"Content-Type": "application/json"}
    index = 'restaurants'
    
    query = {
        "query": {
            "match": {
                "Cuisine": cuisine_key
            }
        },
        "size": 3  # number of rows you want to get in the result
    }
    
    url = host + '/' + index + '/_search'
    result = json.loads(requests.get(url, auth=aws_auth, headers=headers, data=json.dumps(query)).text)
    #result = requests.get(url, auth=aws_auth, headers=headers, data=json.dumps(query))
    dynamoDB_search_keys = []
    for dynamoDB_search_key in result["hits"]["hits"]:
        dynamoDB_search_keys.append(dynamoDB_search_key["_source"]["RestaurantID"])
    # return a list of dynamoDB_search_keys
    return dynamoDB_search_keys
    
    
def dynamoDB_search(dynamoDB_search_key):
        #dynamodb = boto3.resource('dynamodb', region_name=region, endpoint_url="http://localhost:8000")
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('yelp-restaurants')
        response = table.query(
            KeyConditionExpression=Key('Business ID').eq(dynamoDB_search_key)
        )
        
        return response

def send_sms(recommend_info, phone_number):
    sns_client = boto3.client('sns')
    
    response = sns_client.publish(
        PhoneNumber=phone_number,
        Message=recommend_info,
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': 'SENDERID'
            },
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Promotional'
            }
        }
    )
    
    
    
    