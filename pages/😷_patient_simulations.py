from langchain.chains import LLMChain
from langchain.llms import OpenAI
# from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from audio_recorder_streamlit import audio_recorder
import streamlit as st
from collections import defaultdict
from prompts import *
import tempfile
import requests  
import json
import base64
import openai
from openai import OpenAI
client = OpenAI()
import os
import re
from elevenlabs import clone, generate, play, set_api_key, stream
from pathlib import Path
from using_docker import using_docker





st.set_page_config(page_title="AI Patients", page_icon="📖")
st.title("📖 Chat with AI Patients")
st.write("This uses the GPT-3.5-16K Model to allow for lengthier conversations. It is still in beta testing. Please contact David Liebovitz, MD if you have any questions or feedback.")

def autoplay_local_audio(filepath: str):
    # Read the audio file from the local file system
    with open(filepath, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio controls autoplay="false">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )

@st.cache_data
def talk(model, voice, input):
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(    
    base_url="https://api.openai.com/v1",
    api_key=api_key,
)
    return client.audio.speech.create(
                model= model,
                voice = voice,
                input = input,
                )
    
def talk_stream(model, voice, input):
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(    
    base_url="https://api.openai.com/v1",
    api_key=api_key,
)
    response = client.audio.speech.create(
    model= model,
    voice= voice,
    input= input,
    )
    response.stream_to_file("last_message.mp3")



def play_audio_eleven(text, voice="Rachel"):
    set_api_key(st.secrets["ELEVEN_API_KEY"])    

    audio = generate(text=text, voice=voice, stream = False)
    filename = "pt_latest.mp3"
    with open(filename, "wb") as f:
        f.write(audio)  # write the bytes directly to the file

    # st.audio(filename, format='audio/mp3', start_time=0)

    return filename

def play_audio_eleven_all(text, voice="Rachel"):
    set_api_key(st.secrets["ELEVEN_API_KEY"])    

    audio = generate(text=text, voice=voice, stream = False)
    
    

    play(audio, notebook=False, use_ffmpeg=False)
    
    filename = "pt_latest.mp3"
    with open(filename, "wb") as f:
        f.write(audio)  # write the bytes directly to the file

    return filename


def extract_url(text):
    # Use regular expressions to find the URL pattern
    pattern = r"url\":\"(.*?)\""
    match = re.search(pattern, text)
    
    if match:
        # Extract the URL from the matched pattern
        url = match.group(1)
        return url
    else:
        # st.write("Error generating audio... Try again in a moment")
        return None

def extract_url_old(output):
    # Split the output into lines
    lines = output.split('\n')
    
    # Initialize the patient_voice variable
    patient_voice = None

    # Iterate over the lines
    for line in lines:
        # Check if the line starts with 'data:'
        if line.startswith('data:'):
            # Remove 'data:' from the line
            line = line[5:].strip()
            try:
                # Parse the JSON
                data = json.loads(line)
                # Check if the 'url' key is in the data
                if 'url' in data:
                    # Assign the URL to the patient_voice variable
                    patient_voice = data['url']
                    # Break the loop as we've found the URL
                    break
            except json.JSONDecodeError:
                # Handle malformed JSON data
                st.sidebar.write(f"Error parsing JSON data: {line}. Try again in a moment")
                continue
    
    # Return the patient_voice variable
    return patient_voice


def clear_session_state_except_password_correct():
    # Make a copy of the session_state keys
    keys = list(st.session_state.keys())
    
    # Iterate over the keys
    for key in keys:
        # If the key is not 'password_correct', delete it from the session_state
        if key != 'password_correct':
            del st.session_state[key]

def check_password2():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            # del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        if not using_docker:
            st.text_input(
                "Password", type="password", on_change=password_entered, key="password"
            )
            st.write("*Please contact David Liebovitz, MD if you need an updated password for access.*")
            return False
        else:
            st.session_state["password_correct"] = True
            return True
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

def extract_patient_response(text):
    # Look for the phrase 'Patient Response:' in the text
    start = text.find('Patient Response:')
    
    # If 'Patient Response:' is not found, return None
    if start == -1:
        return "Could not find patient response section; please try again!"

    # Remove everything before 'Patient Response:' and strip leading/trailing whitespace
    patient_response = text[start:].strip()

    # Look for the phrase 'Educator Comment:' in the patient_response
    end = patient_response.find('DDx:')

    # If 'Educator Comment:' is found, remove it and everything after it
    if end != -1:
        patient_response = patient_response[:end].strip()

    # # Remove 'Patient Response:' from the patient_response and strip leading/trailing whitespace
    patient_response = patient_response[len('Patient Response:'):].strip()

    # Return the patient_response
    return patient_response


def autoplay_audio(url: str):
    # Download the audio file from the URL
    response = requests.get(url)
    data = response.content
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio controls autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )
    


# def autoplay_local_audio(filepath: str):
#     # Read the audio file from the local file system
#     with open(filepath, 'rb') as f:
#         data = f.read()
#     b64 = base64.b64encode(data).decode()
#     md = f"""
#         <audio controls autoplay="true">
#         <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
#         </audio>
#         """
#     st.markdown(
#         md,
#         unsafe_allow_html=True,
#     )


def transcribe_audio(audio_file_path):
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(    
        base_url="https://api.openai.com/v1",
        api_key=api_key,
    )
    audio_file = open(audio_file_path, "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file, 
    response_format="text"
    )
    return transcript
    # openai.api_base = "https://api.openai.com/v1"
    # openai.api_key = st.secrets["OPENAI_API_KEY"]
    # with open(audio_file_path, 'rb') as audio_file:
    #     transcription = openai.Audio.transcribe("whisper-1", audio_file)
    # return transcription['text']

if "audio_off" not in st.session_state:
    st.session_state["audio_off"] = False

if "audio_input" not in st.session_state:
    st.session_state["audio_input"] = ""
    
if "last_response" not in st.session_state:
    st.session_state["last_response"] = "Patient Response: I can't believe I'm in the Emergency Room feeling sick!"

if st.secrets["use_docker"] == "True" or check_password2():
    st.info("Enter your questions at the bottom of the page or choose the Microphone option. You may ask multiple questions at once. Have fun practicing!")
    system_context = st.radio("Select an AI patient who comes to the ED with:", ("severe headache", "chest pain", "bloody diarrhea", "random symptoms", "You choose!"), horizontal = True, index=0)
    

        
    if system_context == "severe headache":
        template = headache_pt_template
        voice = 'alloy'

    if system_context == "chest pain":
        template = chest_pain_pt_template
        voice = 'echo'

    if system_context == "bloody diarrhea":
        template = bloody_diarrhea_pt_template
        voice = 'fable'
        
    if system_context == "random symptoms":
        template = random_symptoms_pt_template
        voice = 'onyx'

    if system_context == "You choose!":
        symptoms = st.text_input("Enter a list of symptoms separated by commas", placeholder="e.g. fever, cough, headache after returning from a trip to Africa")
        # Create a defaultdict that returns an empty string for missing keys
        template = f'Here are the symptoms: {symptoms} and respond according to the following template:' + chosen_symptoms_pt_template
        voice = 'nova'
        
    if st.button("Set a Scenario"):
        clear_session_state_except_password_correct()
        st.session_state["last_response"] = "Patient Response: I can't believe I'm in the Emergency Room feeling sick!"
        
        


    st.write("_________________________________________________________")

    # Set up memory
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    memory = ConversationBufferMemory(chat_memory=msgs)
    if len(msgs.messages) == 0:
        msgs.add_ai_message("I can't believe I'm in the ER!")

    # view_messages = st.expander("View the message contents in session state")

    # Get an OpenAI API Key before continuing
    if "OPENAI_API_KEY" in st.secrets:
        openai_api_key = st.secrets.OPENAI_API_KEY
    else:
        openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Enter an OpenAI API Key to continue")
        st.stop()

    input_source = st.radio("Input source", ("Text", "Microphone"), index=0)
    st.session_state.audio_off = st.checkbox("Turn off voice generation", value=False) 
    




    prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)
    llm_chain = LLMChain(llm=ChatOpenAI(openai_api_key=openai_api_key, model = "gpt-3.5-turbo-1106"), prompt=prompt, memory=memory)

    # Render current messages from StreamlitChatMessageHistory
    for msg in msgs.messages:
        st.chat_message(msg.type).write(msg.content)

    # If user inputs a new prompt, generate and draw a new response
    if input_source == "Text":
    
        if prompt := st.chat_input():
            st.chat_message("user").write(prompt)
            # Note: new messages are saved to history automatically by Langchain during run
            openai.api_base = "https://api.openai.com/v1"
            openai.api_key = st.secrets["OPENAI_API_KEY"]
            response = llm_chain.run(prompt)
            st.session_state.last_response = response
            st.chat_message("assistant").write(response)
            play = True
            
    else:
        with st.sidebar:
            audio_bytes = audio_recorder(
            text="Click, count to 3 (microphone initializing), and ask a question:",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="user",
            icon_size="3x",
            )
        if audio_bytes:
            # Save audio bytes to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
                fp.write(audio_bytes)
                audio_file_path = fp.name

            # Display the audio file
            # st.session_state.audio_input = st.audio(audio_bytes, format="audio/wav")

            # Transcribe the audio file
            # if st.sidebar.button("Send Audio"):
            prompt = transcribe_audio(audio_file_path)
            st.chat_message("user").write(prompt)
            # Note: new messages are saved to history automatically by Langchain during run
            response = llm_chain.run(prompt)
            st.session_state.last_response = response
            st.chat_message("assistant").write(response)
            play = True

    clear_memory = st.sidebar.button("Start Over")
    if clear_memory:
        # st.session_state.langchain_messages = []
        clear_session_state_except_password_correct()
        st.session_state["last_response"] = "Patient Response: I can't believe I'm in the Emergency Room feeling sick!"
        
    if create_hpi := st.sidebar.button("Create HPI (Wait until you have enough history.)"):    
        openai.api_base = "https://api.openai.com/v1"
        openai.api_key = st.secrets["OPENAI_API_KEY"]    
        hpi = llm_chain.run(hpi_prompt)
        st.sidebar.write(hpi)
            # clear_session_state_except_password_correct()
            # st.session_state["last_response"] = "Patient Response: I can't believe I'm in the Emergency Room feeling sick!"
    # Audio response section 
    # Define the URL and headers
    
    if st.session_state.audio_off == False:
    
        if play == True:
            patient_section = extract_patient_response(st.session_state.last_response)
            audio_path = "last_message.mp3"
            if patient_section is not None and len(patient_section) > 5:
                with st.spinner("Generating audio..."):
                    audio_response = talk_stream("tts-1", voice, patient_section)
                    # audio_response.stream_to_file(audio_path)
                autoplay_local_audio(audio_path)
                st.info("Audio generated by AI!")
                play = False
            
            
            
            # patient_section = extract_patient_response(st.session_state.last_response)
            
            # # Trying elevenlabs
            # link_to_audio = play_audio_eleven(patient_section, voice=voice)
            
            # if link_to_audio:
            # #     # stopping autoplay to try elevenlabs
            #     autoplay_local_audio(link_to_audio)
