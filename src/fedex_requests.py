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