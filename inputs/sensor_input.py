from pydantic import BaseModel


class SensorInput(BaseModel):
    name: str
    description: str
