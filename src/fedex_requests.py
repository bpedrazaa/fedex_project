import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
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

# /////////////////////////////////////////////////////////////////////////////

# Function to change state of package to embarked
def fedexPutEmbarked(event, context):
    
    # Get the package id from the path
    path = event["path"]
    array_path = path.split("/")
    package_id = array_path[-2]
    
    # Get the info of the package
    response = table.get_item(
        Key={
            'pk': package_id,
            'sk': package_id
        }
    )
    
    # Verify if the response is not empty, send error message if is empty
    return_value = ""
    if 'Item' in response:
        item = response['Item']
        
        # Verify the last state of the package
        packaged_state = item['packaged']
        if packaged_state == "1" or packaged_state == 1:
            
            # UPDATE the state of the package
            table.update_item(
                Key={
                    'pk': package_id,
                    'sk': package_id
                },
                # Update the previous state and change to the new state
                UpdateExpression='SET packaged = :packaged_state, embarked = :embarked_state',
                ExpressionAttributeValues={
                    ':packaged_state': '0',
                    ':embarked_state': '1'
                }
            )
            return_value = "State of " + package_id + " updated to embarked!"

            # //    Send a message to the client     //
            message = "Dear Customer, your package with the identifier: ***" + package_id + "*** is currently in the EMBARKED state. We will keep you informed"
                 
            response_topic = topic.publish(
                Message=message,
                MessageAttributes={
                    'package_id': {
                        'DataType': 'String',
                        'StringValue': str(package_id)
                    }
                }
            )
            
            return_value = return_value + ", message of state of package sended to the customer"
                
        else:
            return_value = "Bad formation of states of package, the last state should be packaged"
    else:
        return_value = "Item not found in the fedex-table"

    
    return {
        'statusCode': 200,
        'body': json.dumps(return_value)
    }
    
    


# Function to change state of package to Routed
def fedexPutRouted(event, context):
    
    # Get the package id from the path
    path = event["path"]
    array_path = path.split("/")
    package_id = array_path[-2]
    
    # Get the info of the package
    response = table.get_item(
        Key={
            'pk': package_id,
            'sk': package_id
        }
    )
    
    # Verify if the response is not empty, send error message if is empty
    return_value = ""
    if 'Item' in response:
        item = response['Item']
        
        # Verify the last state of the package
        embarked_state = item['embarked']
        if embarked_state == "1" or embarked_state == 1:
            
            # UPDATE the state of the package
            table.update_item(
                Key={
                    'pk': package_id,
                    'sk': package_id
                },
                # Update the previous state and change to the new state
                UpdateExpression='SET embarked = :embarked_state, routed = :routed_state',
                ExpressionAttributeValues={
                    ':embarked_state': '0',
                    ':routed_state': '1'
                }
            )
            return_value = "State of " + package_id + " updated to routed!"

            # //    Send a message to the client     //
            message = "Dear Customer, your package with the identifier: ***" + package_id + "*** is currently in the ROUTED state. We will keep you informed"
                 
            response_topic = topic.publish(
                Message=message,
                MessageAttributes={
                    'package_id': {
                        'DataType': 'String',
                        'StringValue': str(package_id)
                    }
                }
            )
            
            return_value = return_value + ", message of state of package sended to the customer"
                
        else:
            return_value = "Bad formation of states of package, the last state should be embarked"
    else:
        return_value = "Item not found in the fedex-table"

    
    return {
        'statusCode': 200,
        'body': json.dumps(return_value)
    }
def testGETPrice(event, context):
    # Get package from table
    package_id = 'package_id_01'
    customer_id = 'customer_id_01'
    response = table.get_item(
        Key={
            'pk': package_id,
            'sk': customer_id
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

    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }