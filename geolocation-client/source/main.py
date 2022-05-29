#!/usr/bin/env python
import json
import logging
import os
from datetime import datetime

import coloredlogs as coloredlogs
import paho.mqtt.client as mqtt
import pytz
import requests

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
                'schema': 'activity.location',
                'source': msg.topic,
                'title': '',
                'description': '',
                'extra_attributes': {
                    'location': {
                        'latitude': data['lat'],
                        'longitude': data['lon'],
                        'altitude': data.get('alt'),
                        'accuracy': data.get('acc'),
                    },
                },
                'date_on_timeline': datetime.fromtimestamp(data['tst'], pytz.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
            })
            logger.info(f"Geolocation message processed ({data['lat']}, {data['lon']})")
    except:
        logger.exception(f"Cannot process message: {msg.payload}")


def add_entry(entry: dict):
    try:
        access_token_response = requests.post('http://timeline-backend/oauth/token/', data={
            "client_id": os.environ['GEOLOCATION_CLIENT_ID'],
            "client_secret": os.environ['GEOLOCATION_CLIENT_SECRET'],
            "scope": "entry:write",
            "grant_type": "client_credentials",
        }).json()
        timeline_response = requests.post(
            'http://timeline-backend/timeline/entries/',
            json=entry,
            headers={
                "Authorization": f"Bearer {access_token_response['access_token']}",
            }
        )
        timeline_response.raise_for_status()
    except KeyError:
        logger.exception(f"Could not post geolocation on timeline. Unexpected token response: {access_token_response}")
    except:
        logger.exception("Could not post geolocation on timeline")


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.username_pw_set(os.environ['MQTT_USERNAME'], os.environ['MQTT_PASSWORD'])
mqtt_client.connect("mqtt-broker", 1883, 30)
mqtt_client.loop_forever()
