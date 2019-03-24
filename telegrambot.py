from telegram.ext import Updater, CommandHandler, MessageHandler,Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup, Location
from datetime import datetime, timedelta
import requests
import re
import requests
import pandas as pd
import json
import csv
import math




def start(bot, update):
    kb = [[KeyboardButton('/Yes')],
          [KeyboardButton('/No')]]
    kb_markup = ReplyKeyboardMarkup(kb)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Welcome to Parking!\n\nDo you want to find to nearest carpark?",
                     reply_markup=kb_markup)

def hello(bot, update):
    update.message.reply_text('Hello {}! Please press /start to start our service'.format(update.message.from_user.first_name))

def no(bot, update):
    update.message.reply_text('So sorry about that.....\nPlease share your location with us to find the NEAREST CARPARK')

def yes(bot, update):
    update.message.reply_text('Please share us your live location! ')

def location(bot, update):
    message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message

    current_pos = [message.location.latitude, message.location.longitude]
    print(current_pos)

    request = requests.get("https://api.data.gov.sg/v1/transport/carpark-availability")

    data_json = request.json()

    s1 = json.dumps(data_json) #s1 is a str

    d1 = json.loads(s1)
    d1 = d1['items'] #d1 is now a list
    dict = d1[0] 
    #print(1)

    d1 = dict['carpark_data']
    #print(2)
    df = pd.DataFrame(d1)
    #print(3)
    df_location = pd.read_csv('hdb-carpark-information.csv')
    #print(4)


    df_location.set_index('car_park_no',inplace=True)
   

    df_location = df_location.sort_index()
    df_location.head()

    row_count = 0
    for i in df_location.index:
        df['carpark_number'].replace(i, df_location.iloc[row_count]['X,Y Coordinates'],inplace=True)
        row_count = row_count + 1

    print(df['carpark_number'])
    print(df['carpark_number'][5])

    distance = []

    for i in range(20):
        coord_str = df['carpark_number'][i]
        x, y = coord_str.split(',')
        x = float(x)
        y = float(y)
        dist = ((current_pos[0] - x) **2 + (current_pos[1] - y) **2 ) **0.5
        distance.append(dist)
    index = distance.index(min(distance))


    coord_str = df['carpark_number'][index]
    print(1)
    lat, longt = coord_str.split(',')
    print(2)
    lat = float(lat)/10000
    longt = float(longt)/10000
    print(lat,longt)
    #lat = float() #can run float(current_pos[0]+1)
    #longt = float(df['carpark_number'][index])

    bot.sendLocation(chat_id=update.message.chat_id,
                     latitude=lat,
                     longitude=longt)
    print(4)


updater = Updater('829198290:AAF06v0J-JcOuitBj7sPB1KMQ885Vf4gupc')
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('No', no))
updater.dispatcher.add_handler(CommandHandler('Yes', yes))
updater.dispatcher.add_handler(MessageHandler(Filters.location, location, edited_updates=True))

updater.start_polling()
print("Running")
updater.idle()