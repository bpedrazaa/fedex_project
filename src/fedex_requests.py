import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

users_table = os.environ['FEDEX_TABLE']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(users_table)