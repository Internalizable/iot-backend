import asyncio
import json
from datetime import datetime
import asyncio
import asyncio_mqtt as aiomqtt
import pandas as pd

from database import engine
from models.plant import SensorValue, Plant
from utils.websocket_manager import WebSocketManager
from ai.aimodel import AIModel


class MQTTManager:

    def __init__(self, socket_manager: WebSocketManager, model: AIModel):
        self.socket_manager = socket_manager
        self.model = model

    async def connect(self, host):
        async with aiomqtt.Client(host) as client:
            async with client.messages() as messages:
                await client.subscribe("/UA/Project/SmartLand/+/data")
                await client.subscribe("/UA/Project/SmartLand/+/state")

                async for message in messages:
                    print(f"Received message on topic '{message.topic}': {message.payload.decode()}")

                    plant_key = str(message.topic).split('/')[4]
                    action = str(message.topic).split('/')[5]

                    plant = await engine.find_one(Plant, Plant.key == plant_key)

                    if plant is not None:
                        payload_str = message.payload.decode("utf-8")
                        data = json.loads(payload_str)

                        if action == "state":

                            if data["state"] == "startup":
                                plant.state = False
                                plant.online = True
                            elif data["state"] == "shutdown":
                                plant.state = False
                                plant.online = False
                            elif data["state"] == "watering":
                                plant.state = False
                                plant.online = True

                            asyncio.create_task(self.socket_manager.send_message(
                                json.dumps({"type": "state",
                                            "payload": {
                                                "id": str(plant.id),
                                                "state": plant.state,
                                                "online": plant.online
                                            }}), str(plant.id)))

                            await engine.save(plant)

                        else:
                            temperature = float(data["temperature"])
                            humidity = float(data["humidity"])
                            moisture = float(data["moisture"])
                            light = float(data["light"])

                            plant.temperatures.append(SensorValue(value=temperature, timestamp=datetime.now()))
                            plant.humidities.append(SensorValue(value=humidity, timestamp=datetime.now()))
                            plant.moistures.append(SensorValue(value=moisture, timestamp=datetime.now()))
                            plant.light_values.append(SensorValue(value=light, timestamp=datetime.now()))

                            asyncio.create_task(self.socket_manager.send_message(
                                json.dumps({"type": "data",
                                            "payload": data}), str(plant.id)))

                            xnew = pd.DataFrame([[temperature, humidity, light, moisture]],
                                                columns=['temperature', 'humidity', 'light', 'moisture'])

                            ynew = self.model.predict(xnew)

                            if int(ynew[0]) > 0 and not plant.state:
                                await client.publish("/UA/Project/SmartLand/" + plant.key + "/control", json.dumps({
                                    "state": 1,
                                    "time": int(ynew[0])
                                }))

                                asyncio.create_task(self.socket_manager.send_message(
                                    json.dumps({"type": "state",
                                                "payload": {
                                                    "id": str(plant.id),
                                                    "state": True,
                                                    "online": True
                                                }}), str(plant.id)))

                                plant.state = True

                            await engine.save(plant)
