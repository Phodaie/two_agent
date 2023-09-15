from pydantic import BaseModel , Field
from typing import Optional

class Agent(BaseModel):
    title : str = Field(...,description="Agent's display title")
    role : str = Field(...,description="Agent's role")
    instructions : Optional[str] = Field(default=None , description="Instructions")
    first_message : Optional[str] = Field(default=None)
    content : Optional[str] = Field(default=None)