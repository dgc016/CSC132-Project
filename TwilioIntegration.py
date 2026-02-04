#IN ORDER TO RUN THIS PROGRAM, YOU MUST RUN "pip install twilio" IN YOUR CMD
#most of the data will be pulled from the app, we are just waiting on twilio
#to aprove the application


import os
from twilio.rest import Client
def text(num):
    account_sid = 'null' # this will be pulled from the app
    auth_token = 'null' #this will be pulled from the app 
    client = Client(account_sid, auth_token)
    message = client.messages.create(
      from_='+18559010664',
      body='Hello!',
      to='num'
      )
    print(message.sid)
