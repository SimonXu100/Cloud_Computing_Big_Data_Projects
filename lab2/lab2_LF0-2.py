import json
import boto3
import random
import datetime
from boto3.dynamodb.conditions import Key, Attr

def scan(table, key, value):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)
    response = table.scan(FilterExpression=Attr(key).eq(value))
    return response

def lambda_handler(event, context):
    if 'name' in event and 'phone' in event and 'faceid' in event: # and 'image' in event:
        name=event['name']
        phone=event['phone']
        faceid=event['faceid']
        #image=event['image']
        
        db=boto3.client('dynamodb')
        s3=boto3.client('s3')
        sns=boto3.client('sns')
        
        # response = s3.list_objects(
        #     Bucket='photo-vault-hw2',
        #     Prefix=image
        # )
        # time=response['Contents'][0]['LastModified'].timestamp()
        
        # response = db.put_item(
        #     TableName='visitors',
        #     Item={
        #         'visitor_id': {'S': faceid},
        #         'name':{'S': name},
        #         'phoneNumber':{'S': phone},
        #         'photos':{
        #             'M': {
        #                 'bucket': {'S': 'photo-vault-hw2'},
        #                 'createdTimestamp': {'N': str(time)},
        #                 'objectKey': {'S': image}
        #             },
        #         }
        #     },
        # )
        
        response = db.update_item(
            TableName='visitors',
            Key={
                'visitor_id': {
                    'S': faceid
                }
            },
            AttributeUpdates={
                'name': {
                    'Value': {'S': name},
                    'Action': 'PUT'
                },
                'phoneNumber': {
                    'Value': {'S': phone},
                    'Action': 'PUT'
                },
                'ttl': {
                    'Action': 'DELETE'
                }
            }
        )
        
        # if the visitor already gets an OTP, do nothing
        response=scan('passcodes','visitor_id',faceid)
        if response['Count']==0:
            OTP=''.join([str(random.randint(0, 9)) for _ in range(6)])
            ttl=(datetime.datetime.now()+datetime.timedelta(minutes=5)).timestamp()
            # insert new item in passcodes
            response = db.put_item(
                TableName='passcodes',
                Item={
                    'visitor_id': {'S': faceid}, 
                    'virtual_door_id':{'S':OTP},
                    'ttl':{'N':str(ttl)}
                }
            )
            
            response = sns.publish(
                PhoneNumber=phone,
                Message='Welcome! Your one-time passcode is: '+OTP
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
