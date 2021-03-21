## Smart Door Security
### Description

- Processed streaming video by Kinesis video streams to perform stream analysis to identify faces by Rekognition service.
- Identified known people and provide them with an automatic OTP(one-time passcode) acess code. 
- Triggered an identification workflow(webpages,SNS, restful API) that allows or denies access to unknown visitors, as well as adds them to the database for future training.


Storage:

- DB1: stores temporary access codes(TTL DynamoDB)

- DB2: stores details about the visitors, Index each visitor by the FaceId detected by Amazon Rekognition

- S3(B1): store photos of visitors

WP2: The web page prompts the user to input the OTP for validation 

WP1: The web page collects the name and phone number of the visitor via a web form



Demo Link: 

webpage 1 : https://hw2-wp1.s3.amazonaws.com/index.html

webpage 2:  https://hw2-wp2.s3.amazonaws.com/index.html




### Architecture:
![alt text](../architecture/lab2.png)

