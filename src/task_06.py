import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

# Environment Variables
fedex_table = os.environ['FEDEX_TABLE']

# Initializing dynamo
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(fedex_table)

# Fuction to get the information of a package
def fedexGetPackage(event, context):
    path = event["path"]
    array_path = path.split("/")
    package_id = array_path[-1]
    
    response = table.get_item(
        Key={
            'pk': package_id,
            'sk': package_id
        }
    )
    item = response['Item']
    del item['pk']
    del item['sk']
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET'
        },
        'body': json.dumps(item)
    }