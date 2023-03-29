#!/usr/bin/env python3

import random
from paho.mqtt import client as mqtt_client
from nltk.sentiment import SentimentIntensityAnalyzer
import json
import neopixel
import RPi.GPIO as io
import board
import time

num_pixels = 60
io.setmode(io.BCM)

# Initialize the neopixels object
pixels_pos = neopixel.NeoPixel(board.D21, num_pixels)
pixels_neg = neopixel.NeoPixel(board.D12, num_pixels)
waterPump = 27
poisonPump = 22

io.setup(waterPump, io.OUT)
io.setup(poisonPump, io.OUT)

# Set the color of all neopixels to black
pixels_pos.fill((0, 0, 0))
pixels_pos.show()
pixels_neg.fill((0, 0, 0))
pixels_neg.show()

delay = 0.03

broker = 'io.adafruit.com'
port = 1883
topic = "sarahselby/feeds/rose_piece"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'sarahselby'
password = 'aio_ciZt75e2CiDGrriOGxVLCVCteY5t'
sia = SentimentIntensityAnalyzer()

def activateLed(sentiment):

	print("activateLed function called")

	global pixels_pos
	global pixels_neg
	global waterPump
	global poisonPump

	if sentiment > 0:
		io.output(waterPump, True)
		print("Positive message recieved, green LED activated")
		time.sleep(0.3)
		io.output(waterPump, False)
		# Loop through each neopixel from the far end to the start of the strip
		for i in range(num_pixels-1, -1, -1):
			# Set the color of the current neopixel to white
			pixels_pos[i] = (255, 255, 255)
			pixels_pos.show()
			time.sleep(delay)
			# Set the color of the current neopixel back to black
			pixels_pos[i] = (0, 0, 0)

			# Turn off all neopixels
			pixels_pos.fill((0, 0, 0))
			pixels_pos.show()


	elif sentiment < 0:
		io.output(poisonPump, True)
		print("Negative message recieved, red LED activated")
		time.sleep(0.3)
		io.output(poisonPump, False)
		for i in range(num_pixels-1, -1, -1):
			# Set the color of the current neopixel to white
			pixels_neg[i] = (255, 255, 255)
			pixels_neg.show()
			time.sleep(delay)
			# Set the color of the current neopixel back to black
			pixels_neg[i] = (0, 0, 0)

			# Turn off all neopixels
			pixels_neg.fill((0, 0, 0))
			pixels_neg.show()


# connect to mqtt
def connect_mqtt() -> mqtt_client:
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
    sia_score = sia.polarity_scores(msg)
    print(sia.polarity_scores(msg))
    print(sia_score["compound"])
    if sia_score["compound"] > 0:
        print("result = positive")
        # send to relay here
    else:
        print("result = negative")
        # send to relay here
    activateLed(sia_score["compound"])


def run():
    client = connect_mqtt()
    client.subscribe(topic)
    client.on_message = on_message #attach function to callback
    client.loop_forever()


if __name__ == '__main__':
    run()
