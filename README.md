# Serverless Contact Form on AWS (S3 + API Gateway + Lambda + DynamoDB)

Static contact form website hosted on **Amazon S3**, calling a **Python AWS Lambda** function through **HTTP API Gateway** and storing messages in **Amazon DynamoDB**.  
All resources were created primarily using the **AWS CLI**.

## Architecture

- **S3 bucket**: `ahmedelfar2020` – hosts the static website (`index.html` + `script.js`) using S3 static website hosting.
- **DynamoDB table**: `ContactMessages` – stores contact form submissions.
- **Lambda function**: `saveContactMessage` – Python 3.11 function that validates and stores massages.
- **HTTP API Gateway**: `contact-form-api` – exposes `POST /contact` at the `prod` stage.
- **IAM role**: `lambda-contact-form-role` – Lambda execution role with DynamoDB + CloudWatch permissions.

---

### 1) DynamoDB table

--region us-east-1
--table-name ContactMessages
--attribute-definitions AttributeName=id,AttributeType=S
--key-schema AttributeName=id,KeyType=HASH
--billing-mode PAY_PER_REQUEST

--region us-east-1
--table-name ContactMessages
--query "Table.TableStatus"
--output text

### 2) IAM role for Lambda

`lambda-trust-policy.json`:

{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Principal": { "Service": "lambda.amazonaws.com" },
"Action": "sts:AssumeRole"
}
]
}

role creation:

aws iam create-role
--region us-east-1
--role-name lambda-contact-form-role
--assume-role-policy-document file://lambda-trust-policy.json

managed policies Attachment:

aws iam attach-role-policy
--region us-east-1
--role-name lambda-contact-form-role
--policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy
--region us-east-1
--role-name lambda-contact-form-role
--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam get-role
--region us-east-1
--role-name lambda-contact-form-role
--query "Role.Arn"
--output text

### 3) Lambda function (Python 3.11)

In folder `serverless`:

- Source code: `lambda_function.py`
- Package as ZIP:

Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force

function creation:

aws lambda create-function
--region us-east-1
--function-name saveContactMessage
--runtime python3.11
--handler lambda_function.lambda_handler
--role arn:aws:iam::154292416924:role/lambda-contact-form-role
--timeout 10
--memory-size 128
--zip-file fileb://function.zip

Updating code after changes:

Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force

aws lambda update-function-code
--region us-east-1
--function-name saveContactMessage
--zip-file fileb://function.zip

### 4) HTTP API Gateway (HTTP API v2)

the Creation of HTTP API pointing to Lambda:

aws apigatewayv2 create-api
--region us-east-1
--name contact-form-api
--protocol-type HTTP
--target arn:aws:lambda:us-east-1:154292416924:function:saveContactMessage

Returned `ApiId`: `61hcbnlo43`.

Get `IntegrationId`:

aws apigatewayv2 get-integrations
--region us-east-1
--api-id 61hcbnlo43
--query "Items.IntegrationId"
--output text

e.g. uwcy6l3

the Creation of `POST /contact` route:

aws apigatewayv2 create-route
--region us-east-1
--api-id 61hcbnlo43
--route-key "POST /contact"
--target "integrations/uwcy6l3"

the creation of `prod` stage with auto deploy:

aws apigatewayv2 create-stage
--region us-east-1
--api-id 61hcbnlo43
--stage-name prod
--auto-deploy

Enabling CORS:

aws apigatewayv2 update-api
--region us-east-1
--api-id 61hcbnlo43
--cors-configuration AllowOrigins='["*"]',AllowMethods='["POST","OPTIONS"]',AllowHeaders='["Content-Type"]'

Final endpoint used by the frontend:

https://61hcbnlo43.execute-api.us-east-1.amazonaws.com/prod/contact

### 5) S3 static website

bucket creation:

aws s3 mb s3://ahmedelfar2020 --region us-east-1

Enabling static website hosting:

aws s3 website s3://ahmedelfar2020 --index-document index.html

Uploading frontend files:

aws s3 cp index.html s3://ahmedelfar2020
aws s3 cp script.js s3://ahmedelfar2020

or:
aws s3 sync . s3://ahmedelfar2020/ --acl public-read

Bucket policy for public read:

{
"Version": "2012-10-17",
"Statement": [
{
"Sid": "PublicReadGetObject",
"Effect": "Allow",
"Principal": "",
"Action": ["s3:GetObject"],
"Resource": ["arn:aws:s3:::ahmedelfar2020/"]
}
]
}

Static website endpoint:

http://ahmedelfar2020.s3-website-us-east-1.amazonaws.com

---

## Frontend

- `index.html`: simple contact form (name, email, message).
- `script.js`: sends a JSON `POST` request to API Gateway:

const API_URL =
"https://61hcbnlo43.execute-api.us-east-1.amazonaws.com/prod/contact";

The script displays a success or error message based on the API response.
