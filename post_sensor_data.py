#!/usr/bin/python3
import sys
import time
import json
import board
import requests
import datetime
import argparse
import adafruit_dht

# Create an argument parser
parser = argparse.ArgumentParser(description="Post sensor data to a server")
parser.add_argument("--token", action="store", type=str, help="Authorization Token for the server")
parser.add_argument("--host", action="store", type=str, help="The host server")
parser.add_argument("--sensor", action="store", type=str, help="The sensor tag")

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D16)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

def post_sensor_data(token, host, dateofreading, sensor_tag, temperature, humidity):
    """ Posts sensor data to my server 
    """
    path = "{}/sensors/readings/".format(host)
    payload = json.dumps({
                  "dateofreading": dateofreading,
                  "sensor_tag": sensor_tag,
                  "value_a": temperature,
                  "value_b": humidity
              })
    headers = {
      'Authorization': 'Token {}'.format(token),
      'Content-Type': 'application/json',
    }
    response = requests.request("POST", path, headers=headers, data = payload)

    print(response.text.encode('utf8'))

def main(token, host, sensor_tag):
    help_message = 'post_sensor_data.py -token <token> -h <host> -s <sensor>'

    #This loop will run until the message has been sent. I should perhaps put a time limit on it.
    is_it_sent=False
    while not is_it_sent:
        try:
            # Post the vallues to my server, if it fails, retry until it succeeds
            dateofreading = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            post_sensor_data(token, host, dateofreading, sensor_tag, temperature, humidity)
            is_it_sent = True
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(2.0)

if __name__ == "__main__":
    arr = parser.parse_args()
    main(arr.token, arr.host, arr.sensor)
