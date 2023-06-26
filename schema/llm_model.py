#from pydantic import BaseModel
from enum import Enum

class LlmModelType(str,Enum):
    GPT3_5_TURBO = 'gpt-3.5-turbo'
    GPT4 = 'gpt-4'

    def cost_per_token(self)->tuple[float , float]:
        
        match self:
            case LlmModelType.GPT3_5_TURBO:
                return 0.001 , 0.001
            case LlmModelType.GPT4:
                return 0.001 , 0.001
            
        return 0.001 , 0.001

'''
    def name(self)->str:
        match self:
            case LlmModelType.GPT4:
                return "gpt4"
            case LlmModelType.GPT3_5_TURBO:
                return "gpt3.5-turbo"


'''
#class LlmModel(BaseModel):
#   type : LlmModelType = LlmModelType.GPT3_5_TURBO