import asyncio
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from models.plant import Plant, SensorValue
from utils.websocket_manager import WebSocketManager


class MQTTManager:
    def __init__(self, socket_manager: WebSocketManager):
        self.socket_manager = socket_manager
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    def connect(self, host):
        self.mqtt_client.connect(host)
        self.mqtt_client.loop_start()

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        client.subscribe("UA/Project/SmartLand/+/data")

    def on_message(self, client, userdata, msg):
        plant_key = msg.topic.split('/')[3]
        plant = Plant.objects(key=plant_key).first()

        if plant is not None:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)

            temperature = data["temperature"]
            humidity = data["humidity"]
            moisture = data["moisture"]
            light = data["light"]

            plant.temperatures.append(SensorValue(value=temperature, timestamp=datetime.now()))
            plant.humidities.append(SensorValue(value=humidity, timestamp=datetime.now()))
            plant.moistures.append(SensorValue(value=moisture, timestamp=datetime.now()))
            plant.light_values.append(SensorValue(value=light, timestamp=datetime.now()))

            plant.save()
            asyncio.create_task(self.socket_manager.send_message(payload_str, plant.id))

            # todo implement the AI model here

