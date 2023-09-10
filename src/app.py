# -*- coding: utf-8 -*-
# standard modules
import json
import os
import io

# external modules
import boto3
import pandas as pd
from linebot import LineBotApi
from linebot.models import TextSendMessage

# initial setting
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_BOT_API = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
BUCKET_NAME = os.environ['BUCKET_NAME']
FILE_NAME = 'softbank_hawks.csv'
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
                replyToken = event['events'][0]['replyToken']
                obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
                content = obj['Body'].read().decode('utf-8')
                senshu_df = pd.read_csv(io.StringIO(content))
                print(senshu_df)
                senshuname_list = list(senshu_df['名前'].str.replace('\u3000', ''))
                ouenka_list = list(senshu_df['応援歌'])
                ls_point = list(map(lambda x: ls.culc(input_msg, x) if set(input_msg) & set(x) else 100, senshuname_list))
                if not min(ls_point) == 100:
                    min_index = [i for i, v in enumerate(ls_point) if v == min(ls_point)]
                    msg = ''
                    for i, v in enumerate(min_index):
                        msg += f'【{senshuname_list[v]}】\n{ouenka_list[v]}\n'
                    
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
