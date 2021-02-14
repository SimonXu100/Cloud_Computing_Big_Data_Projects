# python 3.7
import json
import boto3

def lambda_handler(event, context):
    
    client = boto3.client('lex-runtime')
    
    message = ''
    userId = 'default'
    if 'userId' in event:
        userId = event['userId']
    
    if 'query' in event:
        message += event['query'] 
    else:
        message += "empty query."
    
    response = client.post_text(
        botName='DiningConcierge',
        botAlias='dining',
        userId=userId,
        inputText=message
    )

    return {
        'statusCode': 200,
        'headers': {
            #"Access-Control-Allow-Origin": '*' ,
            #"Access-Control-Allow-Headers": "Content-Type",
            #"Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(response['message'])
    }