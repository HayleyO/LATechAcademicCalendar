#Code by Hayley Owens

#######IMPORTS#########
import discord
import datetime
import asyncio
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
########################
#######CONSTANTS########
CHANNELID = 123456789 #you will need your own channel ID this is a temp 
WEBPAGE = "https://events.latech.edu/#!view/day/categories/Academic%20Calendar"
BOTTOKEN = 'Get your own bot token :p'
########################
########GLOBALS#########
client = discord.Client()
########################

###Creates web driver and gets page
def setupWebDriver():
    #Create a web driver for chrome
    driver= webdriver.Chrome(ChromeDriverManager().install())
    #Get web page for academic calendar
    driver.get(WEBPAGE)    
    return driver

###Finds specific part of html and returns that
def parseWebPage(content):
    #Use Beautiful soup HTML parser to split it up to work with
    soup = BeautifulSoup(content, features="html.parser")
    #Find upcoming events tag
    upcomingEvents = []
    upcomingEvents = soup.find('div', attrs={'class':'lw_cal_upcoming_events'}) #Specific find for upcoming events
    return upcomingEvents

###Gets rid of and trims off leftover content from parsing the HTML stuff
def getEventOnly(eventContents):
    index = 0
    events = []
    while(index < len(eventContents)):
        if((index%2)== 1):
            events.append(eventContents[index].text)
        index = index+1
    trimText(events)  
    return events

###Gets rid of leftover html parsed "\n" and replaces it with space
def trimText(events):
    for event in range(len(events)):
        events[event] = str(events[event]).replace('\n', '')
    print(events)

###Goes through list of events and sends them (properly formatted)
async def sendEvents(events):
    channel = client.get_channel(CHANNELID)
    await channel.send("Events for week " + str(datetime.datetime.now().month) + "-" + str(datetime.datetime.now().day) + "-" + str(datetime.datetime.now().year))
    await channel.send("-"*45)
    for event in range(len(events)):
        if(event+1 < len(events) and startsWithDay(events[event+1])):            
            await sendMessage(events[event])
            await channel.send("-"*35)
        else:
            await sendMessage(events[event])

#Feel like this could be improved
###Takes text and sees if it begins with a day of the week
def startsWithDay(text):
    days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]    
    for day in days:
        if text.upper().startswith(day):
            return True
    return False

###Sends a message to the channel, formats it without 'All Day' if that is included
async def sendMessage(text):
    channel = client.get_channel(CHANNELID)
    if text.startswith('All Day'):
        indexOfAllDay = len("All Day")
        substringofEvent = text[indexOfAllDay:]
        await channel.send(substringofEvent)
    else:                
        await channel.send(text)

###############Main###############
async def main():
    while True:
        #Get current day
        #If current day is Sunday (and the stuff hasn't been printed once already) grab the page
        if datetime.datetime.now().weekday() == 7:
            #Create web driver
            driver = setupWebDriver()
            #Take contents from web page
            content = driver.page_source
            #Create html parser and parse content
            upcomingEvents = parseWebPage(content)            
            #Trim so we only get the text of the week's events
            events = getEventOnly(upcomingEvents.contents[3].contents)                              
            await sendEvents(events)
            #Close the web driver
            driver.close()
        await asyncio.sleep(86400) #86400 seconds in a day. Wait one day before checking again.
#################################

########Event Listeners##########
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await main()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if(message.content == "~Clear"):
        async for message in message.channel.history(limit=200):
            await message.delete()
#################################

client.run(BOTTOKEN)