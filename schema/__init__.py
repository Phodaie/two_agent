# For relative imports to work in Python 3.6
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from agent import Agent
from llm_model import LlmModelType
from llm_model import get_completion_from_messages , get_completion_from_function , get_completion_from_function_async , get_completion_anthropic
from settings import TwoAgentsSettings
