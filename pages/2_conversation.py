import openai
import streamlit as st
from schema import LlmModelType, ConversationSettings



st.subheader("Simulation")

openai.api_key = st.secrets["OPENAI_API_KEY"]

settings = ConversationSettings()
model_names = [enum.value for enum in LlmModelType.openAI_models()]

with st.sidebar:
    
    #import settings
    with st.expander("Import Settings"):
        uploaded_file = st.file_uploader("" , key="import_upload")
        if uploaded_file is not None:
            
            bytes_data = uploaded_file.read()
            settings = ConversationSettings.parse_raw(bytes_data)
    
    #temperature
    settings.temperature = st.slider("Temperature", 0.0 ,1.0  ,settings.temperature)

    #LLM model
    model_names = [enum.value for enum in LlmModelType.openAI_models()]
    model_name = st.selectbox('Model', model_names, index=model_names.index(settings.llm_model_type.value))
    selected_model = LlmModelType(model_name)
    settings.llm_model_type = selected_model

    #first message
    settings.first_message = st.text_area('First message', settings.first_message , height=100 , key="first_message_area")
    '''placeholders: <<title>>'''

    #content
    with st.expander("Content"):
        uploaded_file = st.file_uploader("", key="content_upload")
        if uploaded_file is not None:
                settings.content = uploaded_file.read().decode('utf-8')
                print("#############$$$$$$$$$$$$$$%%%%%%%%%%%",uploaded_file.name)
        
        settings.content = st.text_area('', settings.content , height=400 , key="content_area")

        

    #role
    with st.expander("Role"):
        uploaded_file = st.file_uploader("", key="role_upload")
        if uploaded_file is not None:
                settings.role = uploaded_file.read().decode('utf-8')
        
        settings.role = st.text_area('', settings.role , height=400 , key="role_area")
        '''placeholders: <<content>> , <<title>>'''
    
    #role
    with st.expander("Instructions"):
        uploaded_file = st.file_uploader("", key="instructions_upload")
        if uploaded_file is not None:
                settings.role = uploaded_file.read().decode('utf-8')
        
        settings.instructions = st.text_area('', settings.instructions , height=400 , key="instructions_area")
        '''placeholders: <<content>> , <<title>>'''


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [
         {"role": "system", "content": settings.role},
         {"role": "assistant", "content": settings.first_message}
         ]

for message in st.session_state.messages:
    if message["role"] == "system": continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        print(selected_model.value)
        for response in openai.ChatCompletion.create(
            model=selected_model.value,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
