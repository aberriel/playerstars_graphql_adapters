from appsyncclient import AppSyncClient
from uuid import uuid4

import json


cmd = """mutation CreateNotification {
       createNotification (input: {
        entity_id: "%s"
        status: "OPEN"
        notification_complement: "Amanhã tem gol do Gabigol!"
        player_id: "2c8cc35b-cd24-47fb-ad66-e77c15de510a"
      }){
         entity_id
         status
         notification_complement
         player_id
       }  
    }""" % str(uuid4())

query = {'query': cmd}

appsyncclient = AppSyncClient(apiId='3l2u7ok2cjfwdclv5qz3zb5z54', apiKey='da2-xqu7fukowrcilcwoxvcjsrfawm', region='us-east-1')
query_json = json.dumps(query)
response = appsyncclient.execute(data=query_json, callback=None)