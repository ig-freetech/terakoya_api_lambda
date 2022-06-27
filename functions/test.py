from typing import Any
import requests
import json

def lambda_handler(event, context):
    print("event is below")
    print(event)
    
    body = event['body']
    print("body is below")
    print(body)
    
    json_body = json.loads(body)
    
    return {
        "message": json_body['message']
    }

res: requests.Response = requests.get('https://google.com')
print('end')