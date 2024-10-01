import requests
import datetime

testServer = "DISCORD_WEBHOOK_URL"

def SendMessage(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(testServer, data=message)