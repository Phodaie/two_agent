import streamlit as st


import os
import openai
import time
from datetime import datetime
import json

from schema import Agent
from schema import LlmModelType, get_completion_from_messages
from schema import TwoAgentsSettings 
from utility.file_import_export import create_download_link   

#from elevenlabs import clone, generate, play, set_api_key
from elevenlabs.api import History

def main():

    # set_api_key("e78bc29cdc5b72d0760c84e57078786c")

    # audio = generate(
    #     text="Hi! My name is Bella, nice to meet you!",
    #     voice="Bella",
    #     model='eleven_monolingual_v1'
    # )

    #st.audio(data=audio)
    openai.api_key=st.secrets["OPENAI_API_KEY"]   


    aiInstructions = """
    Conduct a casual conversation with a construction worker named {{User.FirstName}} in order to determine how well he/she can identify potential hazards on a construction scenario described in the “Jobsite Scenario” section of the content enclosed in ###Content below. He has already read a description of this scenario.

    Ask him up to 3 questions in order to determine if he can identify the potential hazards in this scenario. Your questions should be only on this scenario.

    Ask him for clarification if you don’t understand his answer. Don’t provide any feedback to him after each question. Just acknowledge his answer and move on.

    Use the material described in the “Sample Fatality Investigation Report” section of the content enclosed in ###Content below to formulate your questions. Don’t make any explicit references to the fatality report.

    Don’t allow the conversation to deviate from the topic of this scenario. Don’t number your questions.

    #IF {{previousSessions}} == true

    Base your conversation on the previous conversation and evaluation of those conversations enclosed in <pre> tags. It should naturally flow from what was covered before. Always ask one question at the time.
    <pre>

    {{Simulation.PreviousSessions}}

    </pre>

    #ENDIF

    ###Content
    {{AI.ReferenceContent}}
    ###

    """ 
    
    st.subheader("Surge9 AI Playground")

    #write aiInstructions to file
    with open("aiInstructions.txt", "w") as text_file:
        text_file.write(aiInstructions) 

    with open("aiInstructions.txt", "r") as text_file:
        aiInstructions = text_file.read()

    st.write(aiInstructions)

def twoAgentTab():
    st.subheader('Two Agent Conversation@')

    settings = TwoAgentsSettings()

    with st.sidebar:

        uploaded_file = st.file_uploader("Import settings")
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            settings = TwoAgentsSettings.parse_raw(bytes_data)



       # UI for agents
        for agent in [settings.agent1 , settings.agent2]:
            with st.expander(agent.title):
                agent.title = st.text_input('Title', agent.title  , key=agent.title)
                agent.role = st.text_area('Role Description', agent.role, height=400)
                if agent.first_message:
                    agent.first_message = st.text_area('First Message', agent.first_message, height=100)
                     

        #UI of other settings      
        settings.temperature = st.slider("Temperature", 0.0 ,1.0  ,settings.temperature)

        model_names = [enum.value for enum in LlmModelType]
        model_name = st.selectbox('Model', model_names, index=model_names.index(settings.llm_model_type.value))
        selected_model = LlmModelType(model_name)


        settings.number_of_turns = st.number_input("Number of exchanges" , settings.number_of_turns , 10)

        start = st.button("Start")
        
        settings.llm_model_type = selected_model
        
        download_settings = create_download_link(settings.json(), 'settings.json', 'Click here to download settings')
        st.markdown(download_settings, unsafe_allow_html=True)

    
    
        
    messages =  [  
    {'role':'system', 'content': settings.agent2.role},    
    {'role':'user', 'content': settings.agent1.first_message},  
    ] 

    
    if start:
        total_cost = 0
        total_seconds = 0
        st.write(f"**{settings.agent1.title}**")
        st.write(messages[1]["content"])

        for i in range(1, settings.number_of_turns):

            st.markdown(f"**{settings.agent1.title if i%2 == 0 else settings.agent2.title}**")
            #st.write(messages)
            start_time = time.time()
            with st.spinner('...'):
                try:
                    response , usage = get_completion_from_messages(messages, temperature=settings.temperature , model=selected_model)
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
            total_seconds += execution_time
            st.write(response)
           
            cost = selected_model.cost(usage)
            total_cost += cost


            st.write(f'*{round(execution_time, 2)} sec , {round(cost, 2)} cents*')

            messages.append({'role':'assistant' if i%2 == 0 else "user" , 'content' : response })
            
            #switch roles
            new_messages = [{'role' :'system' , 'content' : settings.agent2.role if i%2 == 0 else settings.agent1.role}]
            for j in range(1,len(messages)):
                new_message = {'role':'user' if i%2 == 0 else "assistant" , 'content' : messages[j]['content'] }
                new_messages.append(new_message)

            messages = new_messages


        #total cost and time
        minutes, seconds = divmod(total_seconds, 60)
        time_format = f"{minutes:.0f}:{seconds:02.0f}"   
        st.write(f'**total cost : {round(total_cost,2)} cents** in *{time_format} seconds*')

        #download
        download_str = ""
        for i in range(1,len(messages)):
            role = settings.agent2.title if i%2 == 0 else settings.agent1.title
            download_str += f'''{role} : 

{messages[i]['content']}

'''

        filename = 'two agent' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.txt' 
        download_link = create_download_link(download_str, filename, 'Click here to download the conversation')
        st.markdown(download_link, unsafe_allow_html=True)








if __name__ == '__main__':
    
    main()
