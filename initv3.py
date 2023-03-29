#!/usr/bin/env python3

# import random
from paho.mqtt import client as mqtt_client
from nltk.sentiment import SentimentIntensityAnalyzer
import json
import RPi.GPIO as io
import board
import time

io.setmode(io.BCM)

# define the pins for the water and poison pump
waterPump = 27
poisonPump = 22

# set pump pins as outputs
io.setup(waterPump, io.OUT)
io.setup(poisonPump, io.OUT)

# define the MQTT info
broker = 'io.adafruit.com'
port = 1883
topic = "sarahselby/feeds/rose_piece"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'sarahselby'
password = 'xxxxx'
sia = SentimentIntensityAnalyzer()


# function to be called when 
def activateLed(sentiment):

	print("activateLed function called")

	# get the global pump variables to use within function
	global waterPump
	global poisonPump

	# check whether the sentiment of the message was above zero (positive)
	if sentiment > 0:
		# turn water pump on for 0.3 seconds
		io.output(waterPump, True)
		print("Positive message recieved, water pump activated")
		time.sleep(0.3)
		io.output(waterPump, False)
	# if sentiment was below zero (negative)...
	elif sentiment < 0:
		# turn poison pump on for 0.3 seconds
		io.output(poisonPump, True)
		print("Negative message recieved, poison pump activated")
		time.sleep(0.3)
		io.output(poisonPump, False)


# connect to mqtt
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# recieve message
def on_message(client, userdata, message):
    mqtt_dict = json.loads(message.payload.decode()) 
    msg = mqtt_dict["msg"]
    print(msg)
    # do sentiment analysis
    analyse_sentiment(msg)
    

# do sentiment analysis
def analyse_sentiment(msg):
	# get polarity scores using NLTK library
    sia_score = sia.polarity_scores(msg)
    print(sia.polarity_scores(msg))
    # check if compound (combined) score indicates a positive or negative message
    print(sia_score["compound"])
    if sia_score["compound"] > 0:
        print("result = positive")
    else:
        print("result = negative")
    # call function to activate the pumps
    activateLed(sia_score["compound"])


def run():
    client = connect_mqtt()
    client.subscribe(topic)
    client.on_message = on_message #attach function to callback
    client.loop_forever()


if __name__ == '__main__':
    run()
