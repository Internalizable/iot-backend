import asyncio
import json
from datetime import datetime
import asyncio
import asyncio_mqtt as aiomqtt

from database import engine
from models.plant import SensorValue, Plant
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
                    plant = await engine.find_one(Plant, Plant.key == plant_key)

                    if plant is not None:
                        print("is not none")
                        print(plant)
                        payload_str = message.payload.decode("utf-8")
                        print(payload_str)
                        data = json.loads(payload_str)

                        print(data)
                        temperature = data["temperature"]
                        humidity = data["humidity"]
                        moisture = data["moisture"]
                        light = data["light"]

                        plant.temperatures.append(SensorValue(value=temperature, timestamp=datetime.now()))
                        plant.humidities.append(SensorValue(value=humidity, timestamp=datetime.now()))
                        plant.moistures.append(SensorValue(value=moisture, timestamp=datetime.now()))
                        plant.light_values.append(SensorValue(value=light, timestamp=datetime.now()))

                        await engine.save(plant)
                        asyncio.create_task(self.socket_manager.send_message(payload_str, str(plant.id)))

                        # todo implement the AI model here
