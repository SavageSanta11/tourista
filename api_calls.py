import requests
import json
from langchain.utilities import SerpAPIWrapper
from langchain.agents import load_tools
from serpapi import GoogleSearch

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

def getplaces_serp_api(incoming_msg):

    params = {
    "api_key": "7e3b9cc83717ae3f1fdc3a9d91b9a30227580c5d35a1f0164561755ae4fa880a",
    "engine": "google",
    "q": incoming_msg,
    "location": "Boston, Massachusetts, United States",
    "google_domain": "google.com",
    "gl": "us",
    "hl": "en"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    result_places = results['local_results']['places']
    places = []
    places_list = []  

    for place in result_places:
        unit = {}
        title = place['title']
        places.append(title)

        unit['title'] = place['title']
        unit['coordinates'] = place['gps_coordinates']
        places_list.append(unit)

    clean_response = ", ".join(places)
    raw_response = json.dumps({"places": places_list})

    return raw_response, clean_response
    