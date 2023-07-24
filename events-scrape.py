from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import json
import re
import pandas as pd

#import all selenium classes
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

# Create a new instance of the Chrome driver
chrome_path = r"c:\Users\milrushk\Desktop\chromedriver.exe"
service = Service(executable_path=chrome_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

#count for the amount of pages
count = 0



#standardized wait
wait = WebDriverWait(driver, 10)

#go through the links.txt and put in an array
with open('./events-links.txt', 'r') as file:
    event_urls = file.read().split()


category=["food and drink", "music", "health", "business", "travel and outdoor", "community", "fashion", "film and media", "comedy", "DJ and dance"]
index=0

final_array=[]
final_title=[]
#iterate through each event type page
for event in event_urls:
    
    driver.get(event)

    time.sleep(2)

    soup=BeautifulSoup(driver.page_source, features="lxml")
    #holds all the cards
    data_list = []
    data_list = soup.select(selector=".Stack_root__1ksk7")

    event_title=[]
    event_time=[]
    event_location=[]
    event_ticket=[]
    event_host=[]
    event_url=[]
    for card in data_list:

        #get all the titles
        temp_title= card.select(selector='.Typography_body-lg__4bejd')
        for title in temp_title:
            temp1=title.getText()
            event_title.append(temp1)
        
        temp_time=card.select(selector=".Typography_body-md-bold__4bejd.eds-text-color--primary-brand")
        if len(temp_time) == 0:
            event_time.append("None")
        else:
            event_time.append(temp_time[0].getText())
        
        
        temp_location=card.select(selector=".Typography_body-md__4bejd.event-card__clamp-line--one.eds-text-color--ui-600")
        if len(temp_location) == 0:
            event_location.append("None")
        else:
            event_location.append(temp_location[0].getText())

        
        
        temp_ticket = card.select(selector=".Typography_body-md__4bejd.eds-text-color--ui-600")
        temp_ticket2=[]
        
        if len(temp_ticket) == 0:
            temp_ticket2.append("None")
        elif len(temp_ticket) == 1:
            temp_ticket2.append(temp_ticket[0].getText())
        else:
            temp_ticket2.append(temp_ticket[0].getText())
            temp_ticket2.append(temp_ticket[1].getText())
        
        
        temp_ticket3=[]
        for ticket in temp_ticket2:
            if ticket not in event_location:
                temp_ticket3.append(ticket)
                event_ticket.append(ticket)
            
                
        if len(temp_ticket3) == 0:
            event_ticket.append("None")
         
        
        temp_host=card.select(selector=".Typography_body-md-bold__4bejd.eds-text-color--ui-800")
        
        if (len(temp_host)==0):
            event_host.append("None")
        else:
            event_host.append(temp_host[0].getText())
        
        event_url.append(card.a['href'])
    
    #update url way of looping
    # figure out how to deal with none
    #  add urls to the content       
    #  add urls to the content       
    # put final array here if you want data to be separated by categories final_array=[]
    for i in range(len(event_title)):
        
        if event_time[i] == "None":
            final_array.append("The most popular "+ category[index]+ ' event called "' +
             event_title[i]+ '" is happening in Boston this weekend and is hosted at "' + event_location[i] + '" and by "'+ event_host[i] +
            '" with the ticket price: ' + event_ticket[i] + ".")
            final_title.append(event_title[i])
        elif event_location[i] == "None":
            final_array.append("The most popular "+ category[index]+ ' event called "' + event_title[i]+ '" is happening in Boston this weekend at ' +
                       event_time[i] + ' and is hosted by "'+ event_host[i] + '" with the ticket price: ' + event_ticket[i] + "." )
            final_title.append(event_title[i])
        elif event_ticket[i] == "None":
            final_array.append("The most popular "+ category[index]+ ' event called "' + event_title[i]+ '" is happening in Boston this weekend at ' +
                       event_time[i] + ' and is hosted at "' + event_location[i] + '" and by "'+ event_host[i] + "." )
            final_title.append(event_title[i])

        elif event_host[i] == "None":
            final_array.append("The most popular "+ category[index]+ ' event called "' + event_title[i]+ '" is happening in Boston this weekend at ' +
                       event_time[i] + ' and is hosted at "' + event_location[i] + '" with the ticket price: ' + event_ticket[i] + "." )
            final_title.append(event_title[i])

        else:
            final_array.append("The most popular "+ category[index]+ ' event called "' + event_title[i]+ '" is happening in Boston this weekend at ' +
                        event_time[i] + ' and is hosted at "' + event_location[i] + '" and by "'+ event_host[i] + '" with the ticket price: ' + event_ticket[i] + "." )
            final_title.append(event_title[i])
        final_array.append("To find more information about the " + category[index] + " event called " + event_title[i] + ", follow this link: " + event_url[i])
        final_title.append(event_title[i] + ".")
    index+=1
    

#put all of the context in a dataframe ready to be added to the database
# final_df = pd.DataFrame(final_array)
# final_df['title'] = final_title

final_dict = {'title': final_title, 'context': final_array}
final_df = pd.DataFrame(final_dict)
final_df.drop_duplicates(subset='title', keep='first', inplace=True) 
final_csv = final_df.to_csv("event.csv", index = False, sep = "\t")





    