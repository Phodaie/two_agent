#from pydantic import BaseModel
from enum import Enum

class LlmModelType(str,Enum):
    GPT_3_5_TURBO = 'gpt-3.5-turbo-0613'
    GPT_3_5_TURBO_16K = 'gpt-3.5-turbo-16k-0613'
    GPT4 = 'gpt-4-0613'

    def cost(self,usage)->float:
        

        prompt_token_cost = 0
        completion_token_cost = 0
        match self:
            case LlmModelType.GPT_3_5_TURBO:
                prompt_token_cost = 0.0002
                completion_token_cost = 0.00015
            case LlmModelType.GPT4:
                prompt_token_cost = 0.003
                completion_token_cost = 0.006
            case LlmModelType.GPT_3_5_TURBO_16K:
                prompt_token_cost = 0.0003
                completion_token_cost = 0.0004

        prompt_tokens = usage['prompt_tokens']
        completion_tokens = usage['completion_tokens']  
        
        return usage['prompt_tokens'] * prompt_token_cost + usage['completion_tokens'] * completion_token_cost

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