#IN ORDER TO RUN THIS PROGRAM, YOU MUST RUN "pip install twilio" IN YOUR CMD

import os
from twilio.rest import Client
def text(num):
    account_sid = 'null' # add your account SID
    auth_token = 'null' # add your auththenication token
    client = Client(account_sid, auth_token)
    message = client.messages.create(
      from_='+18559010664',
      body='Hello!',
      to='num'
      )
    print(message.sid)
