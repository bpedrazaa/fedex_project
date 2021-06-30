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


#Put Arrived
def fedexPutArrived(event, context):
    print(json.dumps({"running": True}))
    print(json.dumps(event))
    
    path = event["path"]
    array_path = path.split("/")
    package_id = array_path[-2]
    
    #Get item
    response = table.get_item(
        key = 
            {
            'pk': package_id,
            'sk': package_id 
           
            }
        
    )
    
    return_value = ""
    if 'Item' in response:
        item = response['Item']
        
        # Verify the last state of the package
        customer_id = item['customer_id']
        routed_state = item['routed']
        if routed_state == "1" or routed_state == 1 :
            
            # UPDATE the state of the package
            table.update_item(
                Key={
                    'pk': package_id,
                    'sk': package_id
                },
                # Update the previous state and change to the new state
                UpdateExpression='SET routed = :routed_state, arrived = :arrived_state',
                ExpressionAttributeValues={
                    ':routed_state': '0',
                    ':arrived_state': '1'
                }
            )
            return_value = "State of " + package_id + " updated to arrived!"

            # //    Send a message to the client     //
            message = f"Dear Customer. Your identifier is: {customer_id}. Your package with the identifier:  {package_id}  is currently in the ARRIVED state. We will keep you informed"
                 
            response_topic = topic.publish(
                Message=message,
                MessageAttributes={
                    'customer_id': {
                        'DataType': 'String',
                        'StringValue': str(customer_id)
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
    
    
#Put Delivered
def fedexPutDelivered(event, context):
    print(json.dumps({"running": True}))
    print(json.dumps(event))
    
    path = event["path"]
    array_path = path.split("/")
    package_id = array_path[-2]
    
    #Get item
    response = table.get_item(
        key = 
            {
            'pk': package_id,
            'sk': package_id 
           
            }
        
    )
    
    return_value = ""
    if 'Item' in response:
        item = response['Item']
        
        # Verify the last state of the package
        customer_id = item['customer_id']
        arrived_state = item['arrived']
        if arrived_state == "1" or arrived_state == 1 :
            
            # UPDATE the state of the package
            table.update_item(
                Key={
                    'pk': package_id,
                    'sk': package_id
                },
                # Update the previous state and change to the new state
                UpdateExpression='SET arrived = :arrived_state, delivered = : delivered_state',
                ExpressionAttributeValues={
                    ':arrived_state': '0',
                    ':delivered_state': '1'
                }
            )
            return_value = "State of " + package_id + " updated to delivered!"

            # //    Send a message to the client     //
            message = f"Dear Customer. Your identifier is: {customer_id}. Your package with the identifier:  {package_id}  is currently in the DELIVERED state. We will keep you informed"
                 
            response_topic = topic.publish(
                Message=message,
                MessageAttributes={
                    'customer_id': {
                        'DataType': 'String',
                        'StringValue': str(customer_id)
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
    

