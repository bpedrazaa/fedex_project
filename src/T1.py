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
    customer_email = array_path[-1]
    
    body = event["body"]
    body_object = json.loads(body)
    
    packages = table.scan(
    FilterExpression=Attr('pk').contains("package_id_"))
    package_id = 'package_id_' + str(len(packages['Items']) + 1)
#revisamos si el cliente ya esta registrado
    currentCustomer = table.scan(
        FilterExpression=Attr('pk').contains('customer_id_') 
        and Attr('customer_e-mail').eq(customer_email))
#si ya esta registrado customerRegistered sera 0 caso contrario 1
    customerRegistered = len(currentCustomer['Items'])
    print(str(customerRegistered))

    if customerRegistered == 0:
    #revisamos cuantos clientes tenemos para obtner el customer_id correcto 
        registeredCustomers = table.scan(
            FilterExpression=Attr('pk').contains('customer_id_'))
        customer_id = 'customer_id_' + str(len(registeredCustomers['Items']) + 1)
        table.put_item(
            Item={
                'pk': customer_id,
                'sk': customer_id,
                'customer_name': body_object["name"],
                'customer_last_name': body_object["last_name"],
                'customer_e-mail': customer_email,
                'customer_points': '1'
            }
        )
        print("Customer " + customer_email)
        print("Id = customer_id_" + str(customer_id))
        print("Customer Registered Succesfully! ")
        #SNS Subscription
        client = boto3.client('sns')
        response = client.subscribe(
            TopicArn=fedex_topic_arn,
            Protocol='email',
            Endpoint= customer_email,
            Attributes={
                "FilterPolicy": "{\"customer_id\": [\""+customer_id+"\"]}", 
        },
        ReturnSubscriptionArn=True|False)
        print("User subscribed to Fedex-Topic")
    else:
        print("Customer "+ customer_email + "already Registered. Adding points.")
        currentCustomer = table.scan(
            FilterExpression=Attr('pk').contains('customer_id_') 
            and Attr('customer_e-mail').eq(customer_email))
        customer_id = currentCustomer['Items'][0]['pk']
        points = int(currentCustomer['Items'][0]['points'])+1
    
        table.update_item(
            Key={
                'pk': customer_id,
                'sk': customer_id
            },
            # Update the previous state and change to the new state
            UpdateExpression='SET points = :user_points',
            ExpressionAttributeValues={
                ':user_points': str(points)
            })
        print(customer_email+ " has " + str(points) + " points.")

    #Put Package
    table.put_item(
        Item={
            'pk': package_id,
            'sk': package_id,
            'customer_id': customer_id,
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
            'date_arrival': 'undefined',
            'time_arrival': 'undefined', 
            'estimated_price':'undefined'
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Package saved!')
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
    table.update_item(
                Key={
                    'pk': package_id,
                    'sk': package_id
                },
                # Update the previous state and change to the new state
                UpdateExpression='SET packaged = :packaged_state',
                ExpressionAttributeValues={
                    ':packaged_state': '1'
                })
    return_value = "State of " + package_id + " updated to packaged!"

    # //    Send a message to the client     //
    customer_id = response['Item']['customer_id']
    message = f"Dear Customer. Your identifier is: {customer_id}. Your package with the identifier: *** {package_id} *** is currently in the PACKAGED state. We will keep you informed"
                 
                 
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
    return {
        'statusCode': 200,
        'body': json.dumps(str(package_id) + " change to PACKAGED status." )
    }