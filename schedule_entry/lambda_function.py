import boto3
import csv
import datetime
import json
import urllib.parse
import logging
from boto3.dynamodb.conditions import Key
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    '''
    S3に配置されたスケジュールデータをDynamoDBに登録する
    '''
    dynamotable = 'schedule'
    table = dynamodb.Table(dynamotable)
    
    name_key = 'name_record'

    bucket = event['Records'][0]['s3']['bucket']['name']
    filename = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # S3からCSVを取得する
    try: 
        res = s3.get_object(Bucket=bucket, Key=filename)
    except Exception as e:
         return logger.error("Failed to get uploaded file: {}".format(e))

    # 取得したデータを整形する
    if (res['ContentType'] == 'text/csv'):
        body = res['Body'].read()
        bodystr = body.decode('shift-jis', errors="replace")
        lines = bodystr.split('\r\n')[1:]
        reader = csv.reader(lines, delimiter=",", quotechar='"')

        for row in reader:
            name = row[0]
            start_dt = datetime.datetime.strptime(row[1] + row[2], '%Y/%m/%d%H:%M').isoformat() if row[2] else \
                       datetime.datetime.strptime(row[1], '%Y/%m/%d').isoformat()
            end_dt   = datetime.datetime.strptime(row[3] + row[4], '%Y/%m/%d%H:%M').isoformat() if row[4] else \
                       datetime.datetime.strptime(row[3], '%Y/%m/%d').isoformat()
            kind = row[5]
            title = row[6]
            tentative = True if row[7] == 'TRUE' else False 
            unspecified = True if row[8] == 'TRUE' else False 
            all_day = True if row[9] == 'TRUE' else False 
            private = True if row[10] == 'TRUE' else False 
            message = row[11]
            member = [m for m in row[12].split(',')]
            equipment = [e for e in row[13].split(',')]
            print(name, start_dt, end_dt, kind, title, tentative, unspecified, all_day, private, message, member, equipment)
            
            json_data = {'name': name}
            json_data['start_end_title'] = start_dt + '#' + end_dt + '#' + title
            if kind: json_data['kind'] = kind
            json_data['tentative'] = tentative
            json_data['unspecified'] = unspecified
            json_data['all_day'] = all_day
            json_data['private'] = private
            if message: json_data['message'] = message
            if member[0]: json_data['member'] = [ m for m in member ]
            if equipment[0]: json_data['equipment'] = [ e for e in equipment ]
            print('json_data:', json_data)
            
            # name_recordとして登録されていない人がいればDynamoDBに登録する
            try:
                result = table.query(
                    KeyConditionExpression=Key('name').eq(name) & Key('start_end_title').eq(name_key)
                )
            except Exception as e:
                print(e)
            print('result:', result)
            if not result['Count']:
                try:
                    table.put_item(
                        Item = {
                                'name': name,
                                'start_end_title': name_key,
                                'department': filename.split('/')[1].split('.')[0] # 「schedule/」「.csv」を除去
                               }
                    )
                except Exception as e:
                    print(e)
            
            # 予定をDynamoDBに登録
            try:
                table.put_item(
                    Item = json_data
                )
            except Exception as e:
                print(e)
    else:
        logger.error('Invalid File Type: ' + res['ContentType'])
