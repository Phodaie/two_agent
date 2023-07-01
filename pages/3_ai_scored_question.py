import streamlit as st
from pydantic import Field
import openai

from openai_function_call import OpenAISchema
import time
import asyncio
from datetime import datetime
from langchain.llms import OpenAI
from schema import LlmModelType, get_completion_from_messages , get_completion_from_function_async , get_completion_from_function
from schema.settings import AIScoredQuestionSettings
from utility.file_import_export import create_download_link


class FeedbackDetails(OpenAISchema):
    """Answer feedback"""
    feedback: str = Field(..., description="feedback on the answer")
    score: int = Field(..., description="score of the answer")

st.title("AI Scored Questions")

ais_settings = AIScoredQuestionSettings()

model_names = [enum.value for enum in LlmModelType]
with st.sidebar:

    # content = ""
    # role = ""
    # instructions = ""

    #content
    with st.expander("Import/Export Settings"):
        uploaded_file = st.file_uploader("Import Settings")
        if uploaded_file is not None:
                settings_str = uploaded_file.read()
                ais_settings = AIScoredQuestionSettings.parse_raw(settings_str)
        
       
    
    #content
    with st.expander("Content"):
        uploaded_file = st.file_uploader("")
        if uploaded_file is not None:
                content = uploaded_file.read()

    #model selection
    selected_models = [LlmModelType(selected_model_name) for selected_model_name in model_names if st.sidebar.checkbox(selected_model_name, True)]

    #UI for role and instructions
    ais_settings.role = st.text_area('Role', ais_settings.role , height=400)
    
    ais_settings.instructions = st.text_area('Instruction', ais_settings.instructions , height=400)
    '''placeholders: <<content>> , <<question>> , <<answer>>'''

    download_settings = create_download_link(ais_settings.json(), 'settings.json', 'Click here to download settings')
    st.markdown(download_settings, unsafe_allow_html=True)

#question & answer inputs
with st.expander("Question/Answer"):
    ais_settings.question = st.text_area('Question', ais_settings.question , height=200)
    answer = st.text_area('Answer', height=200)
    

evaluate = st.button('Evaluate')

if evaluate:
    #st.write(role)
    #st.write(instructions)
    #role = role.replace("<<question>>" , question)
    for placeholder , value in [("<<content>>" , ais_settings.content) , ("<<question>>" , ais_settings.question) , ("<<answer>>" , answer) ]:
        ais_settings.role = ais_settings.role.replace(placeholder , value)
        ais_settings.instructions = ais_settings.instructions.replace(placeholder , value)

    #st.write(role)
    #st.write(ais_settings.instructions)

    messages =  [  
    {'role':'system', 'content': ais_settings.role},    
    {'role':'user', 'content': ais_settings.instructions},  
    ] 

    tasks = []
    for selected_model in selected_models:
        st.markdown(f"**{selected_model.value}**")
        
        start_time = time.time()
        with st.spinner('...'):
            try:
                #response , usage = asyncio.run( aget_completion_from_messages(messages, temperature=0 , model=selected_model))
                #response , usage = get_completion_from_messages(messages, temperature=0 , model=selected_model)
                
                #response , usage = get_completion_from_function(messages, FeedbackDetails, temperature=0 , model=selected_model)
                response , usage = asyncio.run( get_completion_from_function_async(messages, FeedbackDetails, temperature=0 , model=selected_model))
                #response, usage = await get_completion_from_function_async( messages, FeedbackDetails, temperature=0, model=selected_model)
            
            except openai.error.Timeout as e:
                st.error(f"OpenAI API request timed out: {e}")
                break
            except openai.error.APIError as e:
                st.error(f"OpenAI API returned an API Error: {e}")
                break
            except openai.error.APIConnectionError as e:
                st.error(f"OpenAI API request failed to connect: {e}")
                break
            except openai.error.InvalidRequestError as e:
                st.error(f"OpenAI API request was invalid: {e}")
                break
            except openai.error.AuthenticationError as e:
                st.error(f"OpenAI API request was not authorized: {e}")
                break
            except openai.error.PermissionError as e:
                st.error(f"OpenAI API request was not permitted: {e}")
                break
            except openai.error.RateLimitError as e:
                st.error(f"OpenAI API request exceeded rate limit: {e}")
                break
            except Exception as e:
                st.error(f"OpenAI API: {e}")
                break
       
        end_time = time.time()
        execution_time = end_time - start_time
        st.write(response.feedback)
        st.write(f"score : {response.score}")

        cost = selected_model.cost(usage)
        st.write(f'*{round(execution_time, 2)} sec , {round(cost, 2)} cents*')




