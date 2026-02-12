import http.client, urllib
from PushoverSecrets import token,user
conn = http.client.HTTPSConnection("api.pushover.net:443")
conn.request("POST", "/1/messages.json",
  urllib.parse.urlencode({
    "token": token,
    "user": user,
    "title": "SmartMail",
    "message": "JUST A TEST",
  }), { "Content-type": "application/x-www-form-urlencoded" })
conn.getresponse()
