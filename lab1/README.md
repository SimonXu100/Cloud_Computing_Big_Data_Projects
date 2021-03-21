## Dining Concierge Agent
### Description
- Implement and host a chat user interface on AWS S3, integrating a resful chat APIs built from swagger specification on AWS API Gateway. 

- Train and deploy the Lex chatbot for the purpose of dining concierge agent, extracting and then pushing customer's perferred information into SQS queue.

- Deploy detailed restaurants' information collected from Yelp API on Amazon DynamoDB, combining with Elasticsearch service to optimize searching mechanism.

- Built suggestion mode(Lambda) asychronously operating SQS message queue, retrieving recommended restaurants and cuisines and notifying customers by SNS services. And set up a CloudWatch event trigger to automate the request processing.






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
![alt text](../architecture/lab1.png)