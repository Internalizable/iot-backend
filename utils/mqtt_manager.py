import asyncio
import json
from datetime import datetime
from database import iot
import asyncio
import asyncio_mqtt as aiomqtt

from models.plant import SensorValue
from utils.websocket_manager import WebSocketManager


class MQTTManager:

    def __init__(self, socket_manager: WebSocketManager):
        self.socket_manager = socket_manager

    async def connect(self, host):
        async with aiomqtt.Client(host) as client:
            async with client.messages() as messages:
                await client.subscribe("/UA/Project/SmartLand/+/data")
                async for message in messages:
                    print(message.payload)
                    print(f"Received message on topic '{message.topic}': {message.payload.decode()}")

                    plant_key = str(message.topic).split('/')[4]
                    plant = await iot['plants'].find_one({"key": plant_key})

                    if plant is not None:
                        print("is not none")
                        print(plant)
                        payload_str = message.payload.decode("utf-8")
                        data = json.loads(payload_str)

                        print(data)
                        temperature = data["temperature"]
                        humidity = data["humidity"]
                        moisture = data["moisture"]
                        light = data["light"]

                        plant['temperatures'].append({'value': temperature, 'timestamp': datetime.now()})
                        plant['humidities'].append({'value': humidity, 'timestamp': datetime.now()})
                        plant['moistures'].append({'value': moisture, 'timestamp': datetime.now()})
                        plant['light_values'].append({'value': light, 'timestamp': datetime.now()})

                        await iot['plants'].replace_one({'_id': plant['_id']}, plant)

                        asyncio.create_task(self.socket_manager.send_message(payload_str, str(plant['_id'])))

                        # todo implement the AI model here
