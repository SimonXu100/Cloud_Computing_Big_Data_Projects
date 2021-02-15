import json
import boto3
import email
from sms_spam_classifier_utilities import one_hot_encode
from sms_spam_classifier_utilities import vectorize_sequences

ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
runtime= boto3.client('runtime.sagemaker')

# send email by ses 
def send_email(sender, recipient, aws_region, subject, body_text):
    # The character encoding for the email.
    CHARSET = "UTF-8"
    CONFIGURATION_SET = "ConfigSet"
    
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=aws_region)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender,
            # If you are not using a configuration set, comment or delete the
            # following line
            ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        
def lambda_handler(event, context):
    # s3 put trigger
    s3 = boto3.client("s3")
    file_obj = event["Records"][0]['s3']
    bucket_name, email_path = file_obj['bucket']['name'], s3['object']['key']
    print("filename: ", email_path)
    fileObj = s3.get_object(Bucket = "s1-email-recipt", Key=filename)
    print("file has been gotten!")
    msg = email.message_from_bytes(event["Records"][0]['Body'].read())
    # print(msg['Subject'])
    
    # predict by E1: Prediction Endpoint
    # test_messages = ["FreeMsg: Txt: CALL to No: 86888 & claim your reward of 3 hours talk time to use from your phone now! ubscribe6GBP/ mnth inc 3hrs 16 stop?txtStop"]
    vocabulary_length = 9013
    test_messages = msg['Body'].split("\n").join("")
    one_hot_test_messages = one_hot_encode(test_messages, vocabulary_length)
    encoded_test_messages = vectorize_sequences(one_hot_test_messages, vocabulary_length)
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       ContentType='text/csv',
                                       Body=encoded_test_messages)
    result = json.loads(response['Body'].read().decode())
    score = result['predictions'][0]['score']
    classification = "spam" if score > 0.5 else "ham"
    # contruct reply
    body_text_list.append("We received your email sent at {} with the subject {}".format(msg['Date'], msg['Subject']))
    body_text_list.append("Here is a 240 character sample of the email body: {}".format(msg['Body']))
    body_text_list.append("The email was categorized as {} with a {}% confidence.".format(classification, score))
    body_text = body_text_list.join("\n")
    
    # reply email by SES
    sender = msg['To']
    recipient = msg['From']
    aws_region = "us-east-1"
    subject = msg['Subject']
    body_text=reply_email
    send_email(sender, recipient, aws_region, subject, body_text)
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully label a email as spam or not and reply email.')
    }
