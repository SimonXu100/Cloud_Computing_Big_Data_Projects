## Voice Enabled Photo Album
### Description

- Implement a photo album web application searched using natural language through both text and voice And utilized Lex, ElasticSearch, and Rekognition to create an intelligent search layer to query your photos.

- Built restful API to realize complete workflows consisting of indexing uploaded images based on the labels detected by rekognition and quering photos that handles queries and extract key works by lex.

- Deployed AWS ElasticSearch service and lambda function inside a VPC for security and built code pipeline linked to github repositories that builds and deployes code for the purpose of CI/CD. 

- Created CloudFormation template to represent all the infrastructure resources, speeding up cloud provisioning with infrastructure as code.




Demo Link: https://hw3-wp.s3.amazonaws.com/index.html

### Architecture:
![alt text](../architecture/lab3.png)