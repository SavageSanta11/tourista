import requests
import json

def post_pschat_message(incoming_msg):
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySW5mbyI6eyJpZCI6MjE0MjMsInJvbGVzIjpbImRlZmF1bHQiXSwicGF0aWQiOiI0MTQ4MDM3NS0yNmVhLTRmMDctYThmOS02ZTA5ZmJkMjUxNjIifSwiaWF0IjoxNjg5MzU5NzA1LCJleHAiOjE2OTk3Mjc3MDV9.fuP4FTvBGyqlZ4wtfFiARlF60FGUQsSQMsVjjARMwkU",
        "Content-Type": "application/json"
        } 
    url = "https://api.psnext.info/api/chat"
    data = {
        "message": incoming_msg,
        "options": {
            "model": "gpt35turbo"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    data = response.json()
    message_body = data['data']['messages'][2]['content']
    return message_body


    