import boto3
import json
import logging
from boto3.dynamodb.conditions import Key
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    '''
    DynamoDBから部署を取得する
    '''
    dynamotable = 'schedule'
    table = dynamodb.Table(dynamotable)
    
    name_key = 'name_record'
    
    try:
        result = table.query(
            IndexName='start_end_title-index',
            KeyConditionExpression=Key('start_end_title').eq(name_key)
        )
    except Exception as e:
        print(e)
    
    response = []
    if result:
        for item in result['Items']:
            response.append(item['department'])
    
    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        'body': json.dumps(list(set(response)))
    }
