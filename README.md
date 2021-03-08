# Cloud_Computing_Big_data_Web_projects

## Lab1: Dining Concierge Agent
### Description
- Implemented a chat user interface and host the front end in AWS S3
- Built a Dining Concierge chatbot using Amazon Lex and integrated Lex chatbot into chat API based on API Gateway
Defined chat and recommendation operation using Lambda function and managed chat information in Amazon SQS
- Used the Yelp API to collect 10,000+ restaurants information from Manhattan and deployed those data on Amazon
DynamoDB, combining Elasticsearch service to optimize searching mechanism
- Built suggestion mode by analyzing chat information and Database statistics information, broadcasting recommend
restaurants and cuisines by SNS services. And set up a CloudWatch event trigger to automate request processing








Demo Link: https://hw1-chatbot.s3.amazonaws.com/index.html

Example Iteration:

example Interaction:

User: Hello

Bot: Hi there, how can I help?

User: I need some restaurant suggestions.

Bot: Great. I can help you with that. What city or city area are you looking to dine in?

User: Manhattan

Bot: Got it, Manhattan. What cuisine would you like to try?

User: Japanese

Bot: Ok, how many people are in your party?

User: Two

Bot: A few more to go. What date?

User: Today

Bot: What time?

User: 7 pm, please

Bot: Great. Lastly, I need your phone number so I can send you my findings.

User: 123-456-7890

Bot: You’re all set. Expect my suggestions shortly! Have a good day.

User: Thank you!

Bot: You’re welcome.


### Architecture:
![alt text](architecture/lab1.png)


## Lab2: Smart Door Security
### Description
Demo Link: 

webpage 1 : https://hw2-wp1.s3.amazonaws.com/index.html

webpage 2:  https://hw2-wp2.s3.amazonaws.com/index.html



### Architecture:
![alt text](architecture/lab2.png)







## Lab3: Voice Enabled Photo Album
### Description
Demo Link: https://hw3-wp.s3.amazonaws.com/index.html

### Architecture:
![alt text](architecture/lab3.png)







## Lab4: Intelligent System On Cloud
### Description
Demo Link:  


### Architecture:
![alt text](architecture/lab4.png)
