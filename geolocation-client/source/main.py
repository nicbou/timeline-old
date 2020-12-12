#!/usr/bin/env python
import logging
from datetime import datetime

import coloredlogs as coloredlogs
import paho.mqtt.client as mqtt
import json
import requests
import os


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


def on_connect(client, userdata, flags, rc):
    client.subscribe("+/+/#")
    logger.info(f'MQTT client is connected and listening for messages. Return code was {rc}')


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
        if data['_type'] == 'location':
            add_entry({
                'schema': 'geo.point.current',
                'title': '',
                'description': '',
                'extra_attributes': {
                    'location': {
                        'latitude': data['lat'],
                        'longitude': data['lon'],
                        'altitude': data.get('alt'),
                        'accuracy': data.get('acc'),
                    },
                    'source': msg.topic,
                },
                'date_on_timeline': datetime.fromtimestamp(data['tst']).strftime('%Y-%m-%dT%H:%M:%SZ')
            })
            logger.info(f"Geolocation message processed ({data['lat']}, {data['lon']})")
    except:
        logger.exception(f"Cannot process message: {msg.payload}")


def add_entry(entry: dict):
    url = 'http://timeline-backend/timeline/entries/'
    headers = {'content-type': 'application/json'}
    json_entry = json.dumps(entry)
    requests.post(url, data=json_entry, headers=headers)


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.username_pw_set(os.environ['MQTT_USERNAME'], os.environ['MQTT_PASSWORD'])
mqtt_client.connect("mqtt-broker", 1883, 30)
mqtt_client.loop_forever()
