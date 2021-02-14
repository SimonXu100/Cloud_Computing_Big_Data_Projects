import os
import json
import boto3
import random
import base64
import datetime
import cv2
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

def query(table, key, value):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)
    response = table.query(
        KeyConditionExpression=Key(key).eq(value)
    )
    return response

def scan(table, key, value):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)
    response = table.scan(FilterExpression=Attr(key).eq(value))
    return response

def lambda_handler(event, context):
    # data=[]
    # for record in event['Records']:
    #     cur=base64.b64decode(record['kinesis']['data']).decode()
    #     data.append(str(eval(cur)['FaceSearchResponse']))
    
    # sqs = boto3.resource('sqs')
    # queue = sqs.get_queue_by_name(QueueName='Q1')
    # response = queue.send_message(
    #     MessageBody='\n'.join(data), 
    #     MessageAttributes={}
    # )
    facesearch=eval(base64.b64decode(event['Records'][0]['kinesis']['data']).decode())['FaceSearchResponse']
    if not facesearch:
        return
    matched=facesearch[0]['MatchedFaces']
    # get video
    #record_time=event['Records'][0]['kinesis']['approximateArrivalTimestamp']
    kinesisvideo_client = boto3.client('kinesisvideo')
    response = kinesisvideo_client.get_data_endpoint(
        StreamName='KVS1',
        APIName='GET_HLS_STREAMING_SESSION_URL'
    )
    # kvm_client = boto3.client('kinesis-video-media',endpoint_url=response['DataEndpoint'])
    # response = kvm_client.get_media(
    #     StreamName='KVS1',
    #     StartSelector={
    #         'StartSelectorType': 'PRODUCER_TIMESTAMP',
    #         'StartTimestamp': datetime.datetime.fromtimestamp(record_time)
    #     }
    # )
    kvam_client = boto3.client("kinesis-video-archived-media", endpoint_url=response['DataEndpoint'])
    response = kvam_client.get_hls_streaming_session_url(
        StreamName='KVS1',
        PlaybackMode="LIVE"
    )
    # get frame
    cap = cv2.VideoCapture(response['HLSStreamingSessionURL'])
    ret,frame=cap.read()
    cap.release()
    s3_client=boto3.client('s3')
    response = s3_client.put_object(
        ACL='public-read',
        Body=cv2.imencode('.png', frame)[1].tobytes(),
        Bucket='photo-vault-hw2',
        Key='tmp.png'
    )
    # get faceid
    if matched:
        faceid=matched[0]['Face']['FaceId']
    else:
        rekognition_client=boto3.client('rekognition')
        response = rekognition_client.index_faces(
            CollectionId='faces',
            Image={
                'S3Object': {
                    'Bucket': 'photo-vault-hw2',
                    'Name': 'tmp.png',
                }
            },
            MaxFaces=1,
        )
        if not response['FaceRecords']:
            return
        faceid=response['FaceRecords'][0]['Face']['FaceId']
    # upload to s3
    response = s3_client.list_objects(
        Bucket='photo-vault-hw2',
        Prefix=faceid
    )
    if 'Contents' in response:
        names=[content['Key'] for content in response['Contents']]
        names.sort()
        photo_id=str(int(names[-1].split('.')[0].split('_')[1])+1)
    else:
        photo_id='1'
    photo_name=faceid+'_'+photo_id+'.png'
    response = s3_client.copy_object(
        ACL='public-read',
        Bucket='photo-vault-hw2',
        CopySource={'Bucket': 'photo-vault-hw2', 'Key': 'tmp.png'},
        Key=photo_name
    )
    response = s3_client.delete_object(
        Bucket='photo-vault-hw2',
        Key='tmp.png',
    )
    # s3.Object('photo-vault-hw2',photo_name).copy_from(CopySource='photo-vault-hw2/tmp.png')
    # s3.Object('photo-vault-hw2','tmp.png').delete()
    upload_time=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    # known or unknown
    sns_client=boto3.client('sns')
    db_client=boto3.client('dynamodb')
    
    visitor_response = db_client.get_item(
        TableName='visitors',
        Key={'visitor_id': {'S': faceid}}
    )
    
    known='Item' in visitor_response and visitor_response['Item']['name']['S']!='Unknown'
    photo='https://photo-vault-hw2.s3.amazonaws.com/'+photo_name
    wp1='http://hw2-wp1.s3-website-us-east-1.amazonaws.com?image='+photo_name+'&faceid='+faceid
    
    if known:
        # if the visitor already gets an OTP, do nothing
        response=scan('passcodes','visitor_id',faceid)
        if response['Count']==0:
            OTP=''.join([str(random.randint(0, 9)) for _ in range(6)])
            ttl=(datetime.datetime.now()+datetime.timedelta(minutes=5)).timestamp()
            # insert new item in passcodes
            response = db_client.put_item(
                TableName='passcodes',
                Item={
                    'visitor_id': {'S': faceid}, 
                    'virtual_door_id':{'S':OTP},
                    'ttl':{'N':str(ttl)}
                }
            )
            # update photo in visitors
            response = db_client.update_item(
                TableName='visitors',
                Key={
                    'visitor_id': {
                        'S': faceid
                    }
                },
                AttributeUpdates={
                    'photos': {
                        'Value': {
                            'L': [
                                {'M': 
                                    {
                                    "bucket": {'S': "photo-vault-hw2"},
                                    "createdTimestamp": {'S': upload_time},
                                    "objectKey": {'S': photo_name}
                                    }
                                }
                            ]
                        },
                        'Action': 'ADD'
                    }
                }
            )
            phoneNumber=visitor_response['Item']['phoneNumber']['S']
            response = sns_client.publish(
                PhoneNumber=phoneNumber,
                Message='Welcome! Your one-time passcode is: '+OTP
            )
    else:
        response=query('visitors', 'visitor_id', faceid)
        if response['Count']==0:
            ttl=(datetime.datetime.now()+datetime.timedelta(minutes=5)).timestamp()
            response = db_client.put_item(
                TableName='visitors',
                Item={
                    'visitor_id': {'S': faceid},
                    'name':{'S': 'Unknown'},
                    'phoneNumber':{'S': 'Unknown'},
                    'photos':{
                        'L': [
                            {'M': {
                                'bucket': {'S': 'photo-vault-hw2'},
                                'createdTimestamp': {'S': upload_time},
                                'objectKey': {'S': photo_name}
                                }
                            }
                        ]
                    },
                    'ttl':{'N':str(ttl)}
                },
            )
            
            response = sns_client.publish(
                TopicArn='arn:aws:sns:us-east-1:596817940943:Host',
                Message='A new visitor is trying to gain access permission. The photo of him/her is here: '+photo+'.\nPlease go to the following link to authorize: '+wp1,
            )
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('Hello from Lambda!')
    # }
