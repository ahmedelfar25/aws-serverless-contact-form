import json
import uuid
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("ContactMessages")

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")

        name = body.get("name")
        email = body.get("email")
        message = body.get("message")

        if not (name and email and message):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "name, email, and message are required"})
            }

        item = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "message": message,
            "createdAt": datetime.utcnow().isoformat()
        }

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"success": True})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
