import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import requests

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
    package_id = array_path[-5]
    customer_id = array_path[-3]
    season_id = array_path[-1]
    
    # Get the info about the discounts
    #  Package item
    print(package_id)
    response = table.get_item(
        Key={
            'pk': package_id,
            'sk': package_id
        }
    )
    if "Item" in response: 
        package_dimensions = int(response['Item']['dimensions'])
        package_weight = int(response['Item']['weight'])
    else:
        return {
            'statusCode': 404,
            'body': "The package has not found"
        }   
    #  Customer item
    response = table.get_item(
        Key={
            'pk': customer_id,
            'sk': customer_id
        }
    )
    if "Item" in response: 
        customer_points = int(response['Item']['customer_points'])
    else:
        return {
            'statusCode': 404,
            'body': "The customer has not found"
        } 
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
        season_discount = int(response['Item']['season_discount'])
    
    
    # Calculate customer discount
    if customer_points > 5 and customer_points < 11:
        customer_discount = 10
    elif customer_points > 10:
        customer_discount = 15
    else:
        customer_discount = 0
        
    final_discount = customer_discount + season_discount
    
        
    # Price Calculation
    
    # Get package from table
    
    response = table.get_item(
        Key={
            'pk': package_id,
            'sk': package_id
        }
    )
    package = response['Item']
    # Cities origin and destination
    origin = package['origin']
    destination = package['destination']
    
    # First we search in DB for distance
    response = table.get_item(
        Key={
            'pk': f'city_{origin}',
            'sk': f'city_{destination}'
        }
    )
    if "Item" in response: # If we had already saved the distance we return it
        item = response['Item']
        distance = item['distance']
        distance = int(distance)
    else:
        # Get req to Distance API
        url = f'https://www.distance24.org/route.json?stops={origin}|{destination}'
        distance_info = requests.get(url)
        distance_json = distance_info.json()
        
        # Distance (in KM)
        distance = distance_json['distance']
        
        #Save distance in Cache (DB)
        table.put_item(
                Item={
                    'pk': f'city_{origin}',
                    'sk': f'city_{destination}',
                    'distance': str(distance)
                }
            )
    
    d = distance
    w = package_weight
    v = package_dimensions
    
    #p = max(w*0.5, v/1000)
    p  = (d/100)+max(w*0.5, v/1000)
    
    # Adding discount
    estimated_price = p - ((p/100)*final_discount) 
    
    # Update Price
    table.update_item(
        Key={
            'pk': package_id,
            'sk': package_id
        },
        UpdateExpression='SET estimated_price = :val1',
        ExpressionAttributeValues={
            ':val1': str(estimated_price)
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(estimated_price)
    }