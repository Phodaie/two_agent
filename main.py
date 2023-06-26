import streamlit as st
import base64

import os
import openai
import time
from datetime import datetime
import json

from schema import Agent
from schema import LlmModelType
from schema import Settings 


def main():

    openai.api_key=st.secrets["OPENAI_API_KEY"]
    total_cost = 0

    st.subheader('Two Agent Conversation@')

    settings = Settings()

    with st.sidebar:

        uploaded_file = st.file_uploader("Import settings")
        if uploaded_file is not None:
            
            bytes_data = uploaded_file.read()
            settings = Settings.parse_raw(bytes_data)



        agent1_title = settings.agent1.title

        with st.expander(agent1_title):
            settings.agent1.title = st.text_input('Title', settings.agent1.title  , key=settings.agent1.title)
            settings.agent1.role = st.text_area('Role Description', 
                                       settings.agent1.role, height=400)
            settings.agent1.first_message = st.text_area('First Message',settings.agent1.first_message, height=100)

        #Agent 2

        #agent2_title = settings.agent2.title
        # try:
        #     agent2_title = agent2_title
        # except NameError:
        #     agent2_title = "Agent 2"

        # try:
        #     agent2_role = agent2_role
        # except NameError:
        #     agent2_role = 'You are sales person for Leap9. A SaaS company in micro-learning space. Leap9 main product is called Srge9. Surge9 is a mobile frist micro learning platform with powerful generative AI functionalities. You are answering questions of a potential customer.'

        with st.expander(settings.agent2.title):
            settings.agent2.title = st.text_input('Title', settings.agent2.title , key='agent2_title')
            settings.agent2.role = st.text_area('Role Description', settings.agent2.role,  height=400 , key='settings.agent2.role')
            
        try:
            temperature = settings.temperature
        except NameError:
            temperature = 0.5
        
        settings.temperature = st.slider("Temperature", 0.0 ,1.0  ,settings.temperature)

        # try:
        #     model_name = model_name
        # except NameError:
        #     model_name = 'gpt-3.5-turbo-0613'

        #model_name = st.selectbox('Model', ('gpt-3.5-turbo-0613', 'gpt-4-0613') , index=('gpt-3.5-turbo-0613', 'gpt-4-0613').index(model_name))
        
        #m = [name["value"] for name in LlmModelType.__members__]#
        
        model_names = [enum.value for enum in LlmModelType]
        print(model_names , model_names.index(settings.llm_model_type.value))
        model_name = st.selectbox('Model', model_names, index=model_names.index(settings.llm_model_type.value))
        selected_model = LlmModelType(model_name)

        # try:
        #     number_of_turns = number_of_turns
        # except NameError:
        #     number_of_turns = 3

        settings.number_of_turns = st.number_input("Number of exchanges" , settings.number_of_turns , 10)

        start = st.button("Start")

        #download settings
        # settings = {'agent1_title' : agent1_title,
        #              'agent1_role' : agent1_role, 
        #              'agent2_title' : agent2_title,
        #              'agent2_role' : agent2_role,
        #              'model_name' : selected_model.value,
        #              'temperature' : temperature,
        #              'number_of_turns' : number_of_turns
        #              }
        
        settings.llm_model_type = selected_model
        
                    
        
        download_settings = create_download_link(settings.json(), 'settings.json', 'Click here to download settings')
        st.markdown(download_settings, unsafe_allow_html=True)

    
    
        
    messages =  [  
    {'role':'system', 'content': settings.agent2.role},    
    {'role':'user', 'content': settings.agent1.first_message},  
    ] 

    
    if start:

        st.write(f"**{settings.agent1.title}**")
        st.write(messages[1]["content"])

        for i in range(1, settings.number_of_turns):

            st.markdown(f"**{settings.agent1.title if i%2 == 0 else settings.agent2.title}**")
            #st.write(messages)
            start_time = time.time()
            with st.spinner('...'):
                response , tokens = get_completion_from_messages(messages, temperature=temperature , model=selected_model)
            
            end_time = time.time()
            execution_time = end_time - start_time
            st.write(response)

            per_token_cost_cents , _ = selected_model.cost_per_token()
            # if model_name == 'gpt-3.5-turbo-0613':
            #     per_token_cost_cents = (0.2/1000)
            # elif model_name == 'gpt-4-0613':
            #     per_token_cost_cents = (3/1000)

            cost = round(float(tokens) * per_token_cost_cents , 2)
            total_cost += cost
            st.write(f'*{round(execution_time, 2)} sec , {cost} cents*')

            messages.append({'role':'assistant' if i%2 == 0 else "user" , 'content' : response })
            
            #switch roles
            new_messages = [{'role' :'system' , 'content' : settings.agent2.role if i%2 == 0 else settings.agent1.role}]
            for j in range(1,len(messages)):
                new_message = {'role':'user' if i%2 == 0 else "assistant" , 'content' : messages[j]['content'] }
                new_messages.append(new_message)

            messages = new_messages


        #total cost    
        st.write(f'**total cost : {round(total_cost,2)} cents**')

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




def get_completion_from_messages(messages, 
                                 model=LlmModelType, 
                                 temperature=0, 
                                 max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model.value,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    return (response.choices[0].message["content"] , response["usage"]["total_tokens"])

def create_download_link(string, filename, text):
    # Encode the string as bytes
    string_bytes = string.encode('utf-8')
    
    # Create a base64 representation of the bytes
    base64_str = base64.b64encode(string_bytes).decode('utf-8')
    
    # Create the download link
    href = f'<a href="data:file/txt;base64,{base64_str}" download="{filename}">{text}</a>'
    return href



def serialize_to_json(obj):
    # Convert object to JSON string
    json_string = json.dumps(obj)
    return json_string

def deserialize_from_json(json_string):
    # Convert JSON string to Python object
    obj = json.loads(json_string)
    return obj

if __name__ == '__main__':
    
    main()
