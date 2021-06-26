import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

# Environment Variables
fedex_table = os.environ['FEDEX_TABLE']
fedex_topic_arn = os.environ['TOPIC_ARN']

# Initializing dynamo
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(fedex_table)

# Initializing sns
sns = boto3.resource('sns')
topic = sns.Topic(fedex_topic_arn)

def fedexPutEmbarked(event, context):
    
    # Get the package id from the path
    path = event["path"]
    array_path = path.split("/")
    package_id = array_path[-2]
    
    # Get the info of the package
    #response = table.get_item(
    #    Key={
    #        'pk': package_id,
    #        'sk': package_id
    #    }
    #)
    # Verify if the response is not empty, send error message or not
    #item = response['Item']
    
    # Verify if the last state of the package
    
    # UPDATE the state of the package
    
    # Get the subscriber (email of customer) of the package (work with Thomas, get customer item)
    
    
    # //    Send a message to the client     //
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def fedexPutRouted(event, context):
    print(json.dumps({"running": True}))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }