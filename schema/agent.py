from pydantic import BaseModel

class Agent(BaseModel):
    title : str
    role : str