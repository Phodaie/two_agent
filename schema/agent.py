from pydantic import BaseModel , Field
from typing import Optional

class Agent(BaseModel):
    title : str = Field(...,description="Agent's display title")
    role : str = Field(...,description="Agent's role")
    first_message : Optional[str] = Field(default=None)