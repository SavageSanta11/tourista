from flask import Flask, request, abort
import requests
import json
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route('/', methods=['POST'])
def reset():
    
    incoming_msg = request.values.get('Body','').lower()
    longitude = request.values.get('Longitude','').lower()
    latitude = request.values.get('Latitude','').lower()
   
    #city = 
    resp = MessagingResponse()
   
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySW5mbyI6eyJpZCI6MjE0MTgsInJvbGVzIjpbImRlZmF1bHQiXSwicGF0aWQiOiI1ZjE5ZmQzNS0yOGQyLTRhNjYtYmU5OC1mNjdhZGZiMmUyZTQifSwiaWF0IjoxNjg5MTAzMjY4LCJleHAiOjE2OTk0NzEyNjh9.EFDX15p4b8uxKhJcvwbMo6QUEpWvKKZw8-rOIcgmCUg",
        "Content-Type": "application/json"
        } 
    url = "https://api.psnext.info/api/chat"
    data = {
        "message": incoming_msg,
        "options": {
            "model": "gpt35turbo"
        }
    }
    resp.message("reached")
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=imperial&appid=58cbf43603328cda648836bbdd9dd87c'
    weatherResponse = requests.get(weather_url)
    weatherData = weatherResponse.json()
    temp = weatherData['main']['temp']
    city = weatherData['name']
    feels_like = weatherData['main']['feels_like']
    output = f'Looks like you are in {city} where the current temp is {temp}°F but it feels like {feels_like}°F'
    resp.message(output)

    # if '' in incoming_msg:
    #     response = requests.post(url, headers=headers, data=json.dumps(data))
    #     data = response.json()
    #     content = data['data']['messages'][2]['content']
    
    #     resp.message(content)
    return str(resp), 200, {'Content-Type': 'application/xml'}