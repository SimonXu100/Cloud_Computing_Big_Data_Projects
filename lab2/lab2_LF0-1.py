import json
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    
    OTP = ''
    
    if 'otp' in event:
        OTP = event['otp']
        
    db = boto3.resource('dynamodb')
    table = db.Table('passcodes')
    passcodes = table.query(
        KeyConditionExpression=Key('virtual_door_id').eq(OTP)
    ).get("Items")
    
    visitor_name = ''
    
    if len(passcodes):
        visitor_id = passcodes[0]["visitor_id"]
        
        table = db.Table('visitors')
        visitors = table.query(
            KeyConditionExpression=Key('visitor_id').eq(visitor_id)
        ).get("Items")
        
        if len(visitors):
            visitor_name = visitors[0]["name"]
            
            client=boto3.client('dynamodb')
            response = client.delete_item(
                TableName='passcodes',
                Key={
                    'visitor_id': {
                        'S': visitor_id
                    },
                    'virtual_door_id': {
                        'S': OTP
                    },
                }
            )
   
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": '*' ,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(visitor_name)
    }