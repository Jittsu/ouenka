# -*- coding: utf-8 -*-
# standard modules
import json
import os
import io
import re

# external modules
import boto3
import pandas as pd
from linebot import LineBotApi
from linebot.models import TextSendMessage

# initial setting
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_BOT_API = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
BUCKET_NAME = os.environ['BUCKET_NAME']
FILE_NAMES = {
    'ホークス': 'softbank_hawks.csv',
    'タイガース': 'hanshin_tigers.csv',
    'ライオンズ': 'seibu_lions.csv'
}
s3 = boto3.client('s3')

class levenshtein:

    def __init__(self):
        self.leven_table = []

    def culc(self, str1, str2):
        self.leven_table = [[0 for i in range(len(str1) + 1)] for n in range(len(str2) + 1)]
        for i in range(len(str1) + 1):
            self.leven_table[0][i] = i

        for n in range(len(str2)):
            self.leven_table[n+1][0] = n + 1

        for n in range(len(str2)):
            for i in range(len(str1)):
                if(str2[n] == str1[i]):
                    self.leven_table[n + 1][i + 1] = self.leven_table[n][i]

                else:
                    self.leven_table[n + 1][i + 1] = min(self.leven_table[n][i], self.leven_table[n + 1][i], self.leven_table[n][i + 1])
                    self.leven_table[n + 1][i + 1] += 1

        return self.leven_table[len(str2)][len(str1)]

ls = levenshtein()

def lambda_handler(event, context):
    try:
        if event['events'][0]['type'] == 'message':
            if event['events'][0]['message']['type'] == 'text':
                input_msg = event['events'][0]['message']['text']
                print(f'input word: {input_msg}')
                replyToken = event['events'][0]['replyToken']
                if ('阪神' in input_msg) or ('タイガース' in input_msg):
                    input_msg = re.sub('阪神', '', input_msg)
                    input_msg = re.sub('タイガース', '', input_msg)
                    obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAMES['タイガース'])
                    content = obj['Body'].read().decode('utf-8')
                    senshu_df = pd.read_csv(io.StringIO(content))
                    
                elif ('ソフトバンク' in input_msg) or ('ホークス' in input_msg):
                    input_msg = re.sub('ソフトバンク', '', input_msg)
                    input_msg = re.sub('ホークス', '', input_msg)
                    obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAMES['ホークス'])
                    content = obj['Body'].read().decode('utf-8')
                    senshu_df = pd.read_csv(io.StringIO(content))
                    
                elif ('西武' in input_msg) or ('ライオンズ' in input_msg):
                    input_msg = re.sub('西武', '', input_msg)
                    input_msg = re.sub('ライオンズ', '', input_msg)
                    obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAMES['ライオンズ'])
                    content = obj['Body'].read().decode('utf-8')
                    senshu_df = pd.read_csv(io.StringIO(content))
                    
                else:
                    for i, (k, v) in enumerate(FILE_NAMES.items()):
                        obj = s3.get_object(Bucket=BUCKET_NAME, Key=v)
                        content = obj['Body'].read().decode('utf-8')
                        if i == 0:
                            senshu_df = pd.read_csv(io.StringIO(content))
                            
                        else:
                            tmp = pd.read_csv(io.StringIO(content))
                            senshu_df = pd.concat([senshu_df, tmp])
                            del tmp
                            
                input_msg = re.sub(' ', '', input_msg)
                input_msg = re.sub('　', '', input_msg)
                input_msg = re.sub('\u3000', '', input_msg)
                print(f'search word: "{input_msg}"')
                senshuname_list = list(senshu_df['名前'].str.replace('\u3000', ''))
                ouenka_list = list(senshu_df['応援歌'])
                ls_point = list(map(lambda x: (ls.culc(input_msg, x) if not input_msg in x else 0) if set(input_msg) & set(x) else 100, senshuname_list))
                print(ls_point)
                if not min(ls_point) == 100:
                    min_index = [i for i, v in enumerate(ls_point) if v == min(ls_point)]
                    msg = ''
                    for i, v in enumerate(min_index):
                        msg += f'【{senshuname_list[v]}】\n{ouenka_list[v]}\n'
                    
                    msg = msg[:-1]
                    
                else:
                    msg = '当てはまる選手を見つけられませんでした。'
                    
                LINE_BOT_API.reply_message(replyToken, TextSendMessage(text=msg))
                    
    except Exception as e:
        print(e)
        return {'statusCode': 500, 'body': json.dumps('Exception occurred.')}
                        
                
    return {
        'statusCode': 200,
        'body': json.dumps('Reply ended normally.')
    }
