# For relative imports to work in Python 3.6
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from pydantic import BaseModel

from agent import Agent


class Settings(BaseModel):
    agent1 : Agent
    agent2 : Agent
