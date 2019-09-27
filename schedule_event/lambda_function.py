import boto3
import json
import logging
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta, timezone
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    '''
    DynamoDBからメンバーに対応する予定を取得する
    '''
    dynamotable = 'schedule'
    table = dynamodb.Table(dynamotable)
    
    params = event['queryStringParameters'] if 'queryStringParameters' in event else None
    
    if params:
        response = []
        JST = timezone(timedelta(hours=+9), 'JST')
        year_month = datetime.now(JST).strftime('%Y-%m')
        print('params:', params, 'year_month:', year_month)
        for name in params.values():
            try:
                result = table.query(
                    KeyConditionExpression=Key('name').eq(name) & Key('start_end_title').begins_with(year_month)
                )
                for item in result['Items']:
                    splited = item['start_end_title'].split('#')
                    item['start'] = splited[0]
                    item['end'] = splited[1]
                    item['title'] = splited[2]
                    item['resourceId'] = item['name']
                response.extend(result['Items'])
            except Exception as e:
                print(e)
    
    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        'body': json.dumps(response)
    }
