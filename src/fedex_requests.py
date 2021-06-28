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

def putPackage(event, context):
    # Get the package id from the path
    path = event["path"]
    array_path = path.split("/")
    user_id = array_path[-1]
    
    body = event["body"]
    body_object = json.loads(body)
    #next package id
    packages = table.scan(
        FilterExpression=Attr('pk').contains("package_id_"))
    package_id = len(packages['Items'])
    package_id = package_id + 1
    #number of user records
    user = table.scan(
    FilterExpression=Attr('user_id').eq(user_id))
    userRecords = len(user['Items'])
    #Put Package
    table.put_item(
        Item={
            'pk': 'package_id_' + str(package_id),
            'sk': user_id,
            'customer_id': user_id,
            #putCustomer
            'name': body_object["name"],
            'last_name': body_object["last_name"],
            'customer_e-mail': user_id,
            
            'dimensions': body_object["dimensions"],
            'weight': body_object["weight"],
            'type': body_object["type"],
            'origin': body_object["origin"],
            'destination': body_object["destination"],
            'packaged': '0',
            'embarked': '0',
            'routed': '0',
            'arrived': '0',
            'delivered': '0',
            
            'points': '1',
        }
    )
   
    print("User records= " + str(userRecords))
    if userRecords > 0:
        points = userRecords + 1
        print("User "+ user_id + "already Registered. Adding points.")
        table.update_item(
                Key={
                    'pk': 'package_id_' + str(package_id),
                    'sk': user_id
                },
                # Update the previous state and change to the new state
                UpdateExpression='SET points = :user_points',
                ExpressionAttributeValues={
                    ':user_points': str(points)
                })
        print(user_id + "has " + str(points) + " points.")
    else:
        print("Unregistered User")
        #SNS Subscription
        client = boto3.client('sns')
        response = client.subscribe(
        TopicArn='arn:aws:sns:us-east-1:130637864365:Fedex-Topic',
        Protocol='email',
        Endpoint= user_id,
        Attributes={
            "FilterPolicy": "{\"package_id\": [\"package_id_"+str(package_id)+"\"]}", 
        },
        ReturnSubscriptionArn=True|False)
        print("User subscribed to Fedex-Topic")
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Package saved!' + ' id = package_id_' + str(package_id))
    }
    
def putPackaged(event, context):
    
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
    user_id = table.scan(
    FilterExpression=Attr('pk').eq(package_id))
    table.update_item(
                Key={
                    'pk': package_id,
                    'sk': user_id['Items'][0]['sk']
                },
                # Update the previous state and change to the new state
                UpdateExpression='SET packaged = :packaged_state',
                ExpressionAttributeValues={
                    ':packaged_state': '1'
                })
    return_value = "State of " + package_id + " updated to packaged!"

            # //    Send a message to the client     //
    message = "Dear Customer, your package with the identifier: ***" + package_id + "*** is currently in the PACKAGED state. We will keep you informed"
                 
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
    return {
        'statusCode': 200,
        'body': json.dumps(str(package_id) + " change to PACKAGED status." )
    }