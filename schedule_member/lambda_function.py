import boto3
import json
import logging
from boto3.dynamodb.conditions import Key
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    '''
    DynamoDBから部署に対応するメンバーを取得する
    '''
    dynamotable = 'schedule'
    table = dynamodb.Table(dynamotable)
    
    name_key = 'name_record'
    params = event['queryStringParameters'] if 'queryStringParameters' in event else None
    
    if params:
        join_res = []
        for department in params.values():
            try:
                result = table.query(
                    IndexName='department-index',
                    KeyConditionExpression=Key('department').eq(department)
                )
                join_res.extend(result['Items'])
            except Exception as e:
                print(e)

    response = []
    if result:
        for item in join_res:
            response.append(item['name'])
    
    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        'body': json.dumps(list(set(response)))
    }
