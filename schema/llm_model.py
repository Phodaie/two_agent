import openai
from openai_function_call import OpenAISchema
import asyncio
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import time

class LlmModelType(str,Enum):
    GPT4 = 'gpt-4-0613'
    GPT_3_5_TURBO = 'gpt-3.5-turbo-0613'
    GPT_3_5_TURBO_16K = 'gpt-3.5-turbo-16k-0613'
    

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



def get_completion_from_messages(messages,
                                 model=LlmModelType, 
                                 temperature=0, 
                                 max_tokens=1000):
    
    try:
        response = openai.ChatCompletion.create(
            model=model.value,
            messages=messages,
            temperature=temperature, 
            max_tokens=max_tokens, 
        )
    except:       
        raise

    return (response.choices[0].message["content"] , response["usage"])

def get_completion_from_function(messages,
                                 dataModel,  
                                 model=LlmModelType, 
                                 temperature=0, 
                                 max_tokens=1000):
    

    try:
       
        response = openai.ChatCompletion.create(
            model=model.value,
            functions=[dataModel.openai_schema],
            messages=messages,
            temperature=temperature, 
            max_tokens=max_tokens, 
        )
        
    except:       
        raise

    return dataModel.from_response(response) , response["usage"]

async def get_completion_from_function_async(messages,
                                 dataModel,  
                                 model=LlmModelType, 
                                 temperature=0, 
                                 max_tokens=1000):
    
    start_time = time.time()

    try:
        
        
        response = await openai.ChatCompletion.acreate(
            model=model.value,
            functions=[dataModel.openai_schema],
            messages=messages,
            temperature=temperature, 
            max_tokens=max_tokens, 
        )
    except:       
        raise

    duration = time.time() - start_time
    return dataModel.from_response(response) , response["usage"] , duration

# async def aget_completion_from_messages(messages, 
#                                  model=LlmModelType, 
#                                  temperature=0, 
#                                  max_tokens=1000):
    
#     try:
#         response = openai.ChatCompletion.create(
#             model=model.value,
#             messages=messages,
#             temperature=temperature, 
#             max_tokens=max_tokens, 
#         )
#     except:       
#         raise

#     return (response.choices[0].message["content"] , response["usage"])

# async def aget_completion_from_messages(messages,
#                                             model=LlmModelType,
#                                             temperature=0,
#                                             max_tokens=1000):
#     loop = asyncio.get_event_loop()
#     executor = ThreadPoolExecutor()

#     def run_sync():
#         return openai.ChatCompletion.create(
#             model=model.value,
#             messages=messages,
#             temperature=temperature,
#             max_tokens=max_tokens,
#         )

#     try:
#         response = await loop.run_in_executor(executor, run_sync)
#     except:
#         raise

#     return (response.choices[0].message["content"], response["usage"])
