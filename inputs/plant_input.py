from pydantic import BaseModel


class PlantInput(BaseModel):
    name: str
    description: str
