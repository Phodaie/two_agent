import streamlit as st
import base64

import os
import openai
import time
from datetime import datetime
import json

from schema import Agent
from schema import Settings 


def main():

    openai.api_key=st.secrets["OPENAI_API_KEY"]
    total_cost = 0

    st.subheader('Two Agent Conversation')

    with st.sidebar:

        uploaded_file = st.file_uploader("Import settings")
        if uploaded_file is not None:
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()
            #st.write(bytes_data)

            imported_settings = deserialize_from_json(bytes_data)
            #st.write(imported_settings)
            # To convert to a string based IO:
            #stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            #st.write(stringio)

            # To read file as string:
            #string_data = stringio.read()
            #st.write(string_data)

            agent1_title = imported_settings['agent1_title']
            agent1_role = imported_settings['agent1_role']
            agent2_title = imported_settings['agent2_title']
            agent2_role = imported_settings['agent2_role']
            model_name = imported_settings['model_name']
            temperature = imported_settings['temperature']
            number_of_turns = imported_settings['number_of_turns']
        
        #Agent 1
        try:
            agent1_title = agent1_title
        except NameError:
            agent1_title = "Agent 1"

        try:
            agent1_role = agent1_role
        except NameError:
            agent1_role = '''You work as sr. manager of L&D departement of Divan Manufacturing, a medium size auto part manufacturer.
            Your company wants to deploy a new micro-learning platform and you are responsible for creating a shortlist of products for this purpose.
            For this purpose you are intracting with a sales rep of Leap9. Leap9 sells a micro-learning platform.'''

        with st.expander(agent1_title):
            agent1_title = st.text_input('Title', agent1_title  , key='agent1_title')
            agent1_role = st.text_area('Role Description', 
                                       agent1_role, height=400)
            agent1_firstMessage = st.text_area('First Message', '''
            Hello. Can you give me more information about your product? 
            ''', height=100)

        #Agent 2

        try:
            agent2_title = agent2_title
        except NameError:
            agent2_title = "Agent 2"

        try:
            agent2_role = agent2_role
        except NameError:
            agent2_role = 'You are sales person for Leap9. A SaaS company in micro-learning space. Leap9 main product is called Srge9. Surge9 is a mobile frist micro learning platform with powerful generative AI functionalities. You are answering questions of a potential customer.'

        with st.expander(agent2_title):
            agent2_title = st.text_input('Title', agent2_title , key='agent2_title')
            agent2_role = st.text_area('Role Description', agent2_role,  height=400 , key='agent2_role')
            
        try:
            temperature = temperature
        except NameError:
            temperature = 0.5
        
        temperature = st.slider("Temperature", 0.0 ,1.0  ,temperature)

        try:
            model_name = model_name
        except NameError:
            model_name = 'gpt-3.5-turbo-0613'

        model_name = st.selectbox('Model', ('gpt-3.5-turbo-0613', 'gpt-4-0613') , index=('gpt-3.5-turbo-0613', 'gpt-4-0613').index(model_name))
        
        try:
            number_of_turns = number_of_turns
        except NameError:
            number_of_turns = 3

        number_of_turns = st.number_input("Number of exchanges" , number_of_turns , 10)

        start = st.button("Start")

        #download settings
        settings = {'agent1_title' : agent1_title,
                     'agent1_role' : agent1_role, 
                     'agent2_title' : agent2_title,
                     'agent2_role' : agent2_role,
                     'model_name' : model_name,
                     'temperature' : temperature,
                     'number_of_turns' : number_of_turns
                     }
                    
        
        download_settings = create_download_link(serialize_to_json(settings), 'settings.json', 'Click here to download settings')
        st.markdown(download_settings, unsafe_allow_html=True)

    
    
        
    messages =  [  
    {'role':'system', 'content': agent2_role},    
    {'role':'user', 'content': agent1_firstMessage},  
    ] 

    
    if start:

        st.write(f"**{agent1_title}**")
        st.write(messages[1]["content"])

        for i in range(1, number_of_turns):

            st.markdown(f"**{agent1_title if i%2 == 0 else agent2_title}**")
            #st.write(messages)
            start_time = time.time()
            with st.spinner('...'):
                response , tokens = get_completion_from_messages(messages, temperature=temperature , model=model_name)
            
            end_time = time.time()
            execution_time = end_time - start_time
            st.write(response)

            if model_name == 'gpt-3.5-turbo-0613':
                per_token_cost_cents = (0.2/1000)
            elif model_name == 'gpt-4-0613':
                per_token_cost_cents = (3/1000)

            cost = round(float(tokens) * per_token_cost_cents , 2)
            total_cost += cost
            st.write(f'*{round(execution_time, 2)} sec , {cost} cents*')

            messages.append({'role':'assistant' if i%2 == 0 else "user" , 'content' : response })
            
            #switch roles
            new_messages = [{'role' :'system' , 'content' : agent2_role if i%2 == 0 else agent1_role}]
            for j in range(1,len(messages)):
                new_message = {'role':'user' if i%2 == 0 else "assistant" , 'content' : messages[j]['content'] }
                new_messages.append(new_message)

            messages = new_messages


        #total cost    
        st.write(f'**total cost : {round(total_cost,2)} cents**')

        #download
        download_str = ""
        for i in range(1,len(messages)):
            role = agent2_title if i%2 == 0 else agent1_title
            download_str += f'''{role} : 

{messages[i]['content']}

'''

        filename = 'two agent' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.txt' 
        download_link = create_download_link(download_str, filename, 'Click here to download the conversation')
        st.markdown(download_link, unsafe_allow_html=True)




def get_completion_from_messages(messages, 
                                 model="gpt-3.5-turbo", 
                                 temperature=0, 
                                 max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
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
