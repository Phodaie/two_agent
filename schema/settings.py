# For relative imports to work in Python 3.6
import os, sys
#from tkinter import NO; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from pydantic import BaseModel , Field
from typing import Optional  , ClassVar
from agent import Agent
from llm_model import LlmModelType

class TwoAgentsSettings(BaseModel):
    
    default_role1 : ClassVar[str] = '''You work as sr. manager of L&D departement of Divan Manufacturing, a medium size auto part manufacturer.
            Your company wants to deploy a new micro-learning platform and you are responsible for creating a shortlist of products for this purpose.
            For this purpose you are intracting with a sales rep of Leap9. Leap9 sells a micro-learning platform.
    '''
    
    default_role2 : ClassVar[str] = 'You are sales person for Leap9. A SaaS company in micro-learning space. Leap9 main product is called Srge9. Surge9 is a mobile frist micro learning platform with powerful generative AI functionalities. You are answering questions of a potential customer.'
    

    agent1 : Agent = Agent(title='Agent 1' , role=default_role1 , first_message='Hello. Can you give me more information about your product?' )
    agent2 : Agent = Agent(title='Agent 2' , role=default_role2 , first_message="")

    llm_model_type : LlmModelType = LlmModelType.GPT_3_5_TURBO

    temperature : float = Field(default=0.3, description="Temperature of the LLM")

    number_of_turns : int = Field(default=3, description="Number of message exchanges between the agents")

class AIScoredQuestionSettings(BaseModel):

    role : str = "You are an expert agent."

    instructions : str = "Evaluate the answer \n <<answer>> to the question <<question>>"
    
    question : str = "What is Theory of Mind?"

    content : str = "" 

class ConversationSettings(BaseModel):

    temperature : float = Field(default=0.3, description="Temperature of the LLM")

    llm_model_type : LlmModelType = LlmModelType.GPT_3_5_TURBO

    content : str = Field(default="" , description="Content")

    role : str = Field(default="" , description="Role")

    instructions : str = Field(default="" , description="Instructions")

