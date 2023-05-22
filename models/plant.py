
from datetime import datetime
from typing import List

from odmantic import Model, Field, EmbeddedModel


class SensorValue(EmbeddedModel):
    value: float = Field(required=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Plant(Model):
    name: str = Field(required=True, unique=True)
    description: str = Field(required=True)
    key: str = Field(required=True, unique=True)
    online: bool = Field(required=True, default=False)
    state: bool = Field(required=True, default=False)
    temperatures: List[SensorValue] = Field(default=[])
    humidities: List[SensorValue] = Field(default=[])
    moistures: List[SensorValue] = Field(default=[])
    light_values: List[SensorValue] = Field(default=[])

