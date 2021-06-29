import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# Environment Variables
fedex_table = os.environ['FEDEX_TABLE']
fedex_topic_arn = os.environ['TOPIC_ARN']

# Initializing dynamo
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(fedex_table)

# Initializing sns
sns = boto3.resource('sns')
topic = sns.Topic(fedex_topic_arn)

def fedexPutDiscount(event, context):
    # Get the package id and the customer id from the path
    path = event["path"]
    array_path = path.split("/")
    package_id = array_path[2]
    customer_id = array_path[4]
    season_id = array_path[6]
    
    # Get the info about the discounts
    #  Package item
    try:
        response = table.get_item(
            Key={
                'pk': package_id,
                'sk': package_id
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        package_dimensions = response['Item']['dimensions']
        package_weight = response['Item']['weight']
    #  Customer item
    try:
        response = table.get_item(
            Key={
                'pk': customer_id,
                'sk': customer_id
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        customer_points = response['Item']['customer_points']
    #  Season item
    try:
        response = table.get_item(
            Key={
                'pk': season_id,
                'sk': season_id
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        season_discount = 0
    else:
        season_discount = response['Item']['season_discount']
        
    # Calculate customer discount
    if customer_points > 5 and customer_points < 11:
        customer_discount = 10
    elif customer_points > 10:
        customer_discount = 15
    else:
        customer_discount = 0
        
    final_discount = customer_discount + season_discount
        
    # Price Calculation
    
    ########### aquí lo de Distance ###########
    
    # d = something
    w = package_weight
    v = package_dimensions
    
    p = max(w*0.5, v/1000)
    #p  = (d/100)+max(w*0.5, v/1000)
    
    # Adding discount
    estimated_price = p - ((p/100)*final_discount) 
    
    return {
        'statusCode': 200,
        'body': json.dumps(estimated_price)
    }