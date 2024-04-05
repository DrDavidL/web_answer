import streamlit as st
import openai
import os  
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain, create_extraction_chain_pydantic
from langchain.prompts import ChatPromptTemplate
from extract_prompts import *
import openai
import time
from openai import OpenAI
import json

from pydantic import BaseModel, Field

class OncologyDiagnosis(BaseModel):
    last_name: str = Field(..., description="Patient's last name")
    first_name: str = Field(..., description="Patient's first name")
    age: int = Field(..., description="Patient's age")
    sex: str = Field(..., description="Patient's sex") 
    diagnosis_type: str = Field(..., description="Type of cancer")
    diagnosis_date: str = Field(..., description="Date of diagnosis")
    cancer_tests: str = Field(..., description="Cancer tests conducted")
    treatments: str = Field(..., description="Treatments for the cancer")
    medication: bool = Field(..., description="Indicates if medication is prescribed")
    medication_details: str = Field(..., description="Details of prescribed medication")
    chemotherapy: bool = Field(..., description="Indicates if chemotherapy is prescribed")
    chemotherapy_details: str = Field(..., description="Details of chemotherapy")
    surgery: bool = Field(..., description="Indicates if surgery was performed")
    surgery_details: str = Field(..., description="Details of surgery")
    alcohol_use: str = Field(..., description="Alcohol use")
    tobacco_history: str = Field(..., description="Tobacco history")


def old_method3(string, model="gpt-3.5-turbo", output = "json") -> OncologyDiagnosis:
    client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
    response=  client.chat.completions.create(
      model=model,
      response_model=OncologyDiagnosis,
      messages=[
          {
              "role": "user",
              "content": f"Get user details for {string}",
          },
      ],
    )  # type: ignore
    return json.dumps(response.dict(), indent=2)
  
  
def method3(string, model="gpt-3.5-turbo", output = "json") -> OncologyDiagnosis:
    client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
    response=  client.chat.completions.create(
      model=model,
      messages=[
          ({"role": "system", "content": system_prompt}),
          {
              "role": "user",
              "content": f"Here is the note: {string}",
          },
      ],
  )  # type: ignore
    return response.choices[0].message.content

def is_valid_api_key(api_key):
    openai.api_key = api_key

    try:
         # Send a test request to the OpenAI API
        response = openai.Completion.create(model="text-davinci-003",
                  prompt="Hello world")['choices'][0]['text']
        return True
    except Exception:
        pass

    return False

def fetch_api_key():
    api_key = None

    
    try:
         # Attempt to retrieve the API key as a secret
         api_key = st.secrets["OPENAI_API_KEY"]
         st.session_state.openai_api_key = api_key
         os.environ['OPENAI_API_KEY'] = api_key
    except KeyError:


        if st.session_state.openai_api_key != '':
            api_key = st.session_state.openai_api_key
            os.environ['OPENAI_API_KEY'] = api_key
            # If the API key is already set, don't prompt for it again
            # st.write(f'Here is what we think the key is step 2: {api_key}')
            return api_key
        else:        
            # If the secret is not found, prompt the user for their API key
            st.warning("Oh, dear friend of mine! It seems your API key has gone astray, hiding in the shadows. Pray, reveal it to me!")
            api_key = st.text_input("Please, whisper your API key into my ears: ", key = 'warning')
  
            st.session_state.openai_api_key = api_key
            os.environ['OPENAI_API_KEY'] = api_key
            # Save the API key as a secret
            # st.secrets["my_api_key"] = api_key
            # st.write(f'Here is what we think the key is step 3: {api_key}')
            return api_key
    
    return api_key

@st.cache_data
def answer_using_prefix(prefix, sample_question, sample_answer, my_ask, temperature, history_context):
    client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
    # history_context = "Use these preceding submissions to address any ambiguous context for the input weighting the first three items most: \n" + "\n".join(st.session_state.history) + "now, for the current question: \n"
    completion = client.chat.completions.create( # Change the function Completion to ChatCompletion
    # model = 'gpt-3.5-turbo',
    model = st.session_state.model,
    messages = [ # Change the prompt parameter to the messages parameter
            {'role': 'system', 'content': prefix},
            {'role': 'user', 'content': sample_question},
            {'role': 'assistant', 'content': sample_answer},
            {'role': 'user', 'content': my_ask + history_context}
    ],
    temperature = temperature,
    stream = False)   
    # )
    # start_time = time.time()
    # delay_time = 0.01
    # answer = ""
    # full_answer = ""
    # c = st.empty()
    
    # for event in completion:


    #     c.markdown(answer)
    #         # full_answer += answer
    #     event_time = time.time() - start_time
    #     event_text = event['choices'][0]['delta']
    #     answer += event_text.get('content', '')
    #     full_answer += event_text.get('content', '')
    #     time.sleep(delay_time)
    # # st.write(history_context + prefix + my_ask)
    # # st.write(full_answer)
    #     st.session_state.copied_note = full_answer
    return completion.choices[0].message.content
    # st.write(gen_note) # Display the generated note

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
         """Checks whether a password entered by the user is correct."""
         if st.session_state["password"] == st.secrets["password"]:
             st.session_state["password_correct"] = True
             del st.session_state["password"]  # don't store password
         else:
             st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.write("*Please contact David Liebovitz, MD if you need an updated password for access.*")
        return False
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

if 'copied_note' not in st.session_state:
    st.session_state.copied_note = ''

default_schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "patientInformation": {
      "type": "object",
      "properties": {
        "patientID": {
          "type": "string"
        },
        "dateOfBirth": {
          "type": "string",
          "format": "date"
        },
        "gender": {
          "type": "string"
        },
        "ethnicity": {
          "type": "string"
        },
        "smokingStatus": {
          "type": "string"
        },
        "familyHistory": {
          "type": "string"
        }
      },
      "required": ["patientID", "dateOfBirth", "gender"]
    },
    "cancerDiagnosis": {
      "type": "object",
      "properties": {
        "diagnosisDate": {
          "type": "string",
          "format": "date"
        },
        "cancerType": {
          "type": "string"
        },
        "cancerStage": {
          "type": "string"
        },
        "histologicalGrade": {
          "type": "string"
        },
        "primarySite": {
          "type": "string"
        },
        "metastasisSites": {
          "type": "string"
        },
        "symptoms": {
          "type": "string"
        },
        "imagingFindings": {
          "type": "string"
        },
        "laboratoryResults": {
          "type": "string"
        },
        "molecularMarkers": {
          "type": "string"
        }
      },
      "required": ["diagnosisDate", "cancerType", "cancerStage", "primarySite", "symptoms"]
    },
    "treatmentInformation": {
      "type": "object",
      "properties": {
        "treatmentType": {
          "type": "string"
        },
        "treatmentStartDate": {
          "type": "string",
          "format": "date"
        },
        "treatmentEndDate": {
          "type": "string",
          "format": "date"
        },
        "treatmentResponse": {
          "type": "string"
        },
        "sideEffects": {
          "type": "string"
        },
        "chemotherapy": {
          "type": "string"
        },
        "radiationTherapy": {
          "type": "string"
        },
        "surgery": {
          "type": "string"
        },
        "targetedTherapy": {
          "type": "string"
        },
        "immunotherapy": {
          "type": "string"
        },
        "clinicalTrialEnrollment": {
          "type": "string"
        }
      },
      "required": ["treatmentType", "treatmentStartDate", "treatmentEndDate", "treatmentResponse"]
    },
    "followUpInformation": {
      "type": "object",
      "properties": {
        "lastFollowUpDate": {
          "type": "string",
          "format": "date"
        },
        "diseaseStatus": {
          "type": "string"
        },
        "progressionInformation": {
          "type": "string"
        },
        "performanceStatus": {
          "type": "string"
        },
        "toxicityAssessment": {
          "type": "string"
        },
        "cancerRelatedSymptoms": {
          "type": "string"
        },
        "qualityOfLife": {
          "type": "string"
        }
      },
      "required": ["lastFollowUpDate", "diseaseStatus", "performanceStatus"]
    }
  },
  "required": ["patientInformation", "cancerDiagnosis", "treatmentInformation", "followUpInformation"]
}

   
old_schema1 = {
"properties": {
    "patient_name": {"type": "string"},
    "age_at_visit": {"type": "integer"},
    "cancer_type": {"type": "string"},
    "age_at_diagnosis": {"type": "integer"},
    "treatment_history": {"type": "array"},
    "recurrence_status": {"type": "boolean"},
    "age_at_recurrence": {"type": "integer"},
    "recurrence_treatment": {"type": "array"},
},
"required": ["patient_name", "age_at_visit", "cancer_type", "age_at_diagnosis"],
}

schema2 = {
    "properties": {
        "patient_last_name": {"type": "string"},
        "patient_first_name": {"type": "string"},
        "age_at_cancer_diagnosis": {"type": "integer"},
        "age_at_cancer_recurrence": {"type": "integer"},
        "age_at_visit": {"type": "integer"},
        "specific_cancer_type": {"type": "string"},
        "cancer_stage_at_diagnosis": {"type": "string"},
        "cancer_treatment_history": {"type": "string"},
        "cancer_treatment_current": {"type": "string"},
        "cancer_recurrence_status": {"type": "string"},
        "cancer_recurrence_date": {"type": "string"},
        "cancer_recurrence_treatment": {"type": "string"},
        "cancer_current_status": {"type": "string"},
        "cancer_current_status_date": {"type": "string"},
        "cancer_current_status_details": {"type": "string"},
        "cancer_symptoms": {"type": "string"},
        "performance_status": {"type": "string"},
        "imaging_findings": {"type": "string"},
        "laboratory_results": {"type": "string"},
        "comorbidities": {"type": "string"},
        "quality_of_life": {"type": "string"},
    },
    "required": ["patient_last_name", "patient_first_name"],
}
schema3 = {
    "properties": {
        "patient_last_name": {"type": "string"},
        "patient_first_name": {"type": "string"},
        "patient_age": {"type": "integer"},
        "patient_sex": {"type": "string"},
        "race": {"type": "string"},
        "cancer_type": {"type": "string"},
        "cancer_stage": {"type": "string"},
        "histology": {"type": "string"},
        "tumor_grade": {"type": "string"},
        "primary_site": {"type": "string"},
        "metastasis_sites": {"type": "string"},
        "diagnosis_date": {"type": "string"},  # ISO date format (yyyy-mm-dd) is recommended
        "diagnosis_method": {"type": "string"},
        "biomarkers": {"type": "string"},
        "genetic_mutations": {"type": "string"},
        "symptoms": {"type": "string"},
        "comorbidities": {"type": "string"},
        "surgery": {"type": "string"},
        "chemotherapy": {"type": "string"},
        "radiation_therapy": {"type": "string"},
        "immunotherapy": {"type": "string"},
        "targeted_therapy": {"type": "string"},
        "hormone_therapy": {"type": "string"},
        "treatment_start_date": {"type": "string"},  # ISO date format (yyyy-mm-dd) is recommended
        "treatment_end_date": {"type": "string"},  # ISO date format (yyyy-mm-dd) is recommended
        "treatment_response": {"type": "string"},
        "adverse_events": {"type": "string"},
        "supportive_care": {"type": "string"},
        "palliative_care": {"type": "string"},
        "clinical_trials": {"type": "string"},
        "follow_up_plan": {"type": "string"},
        "patient_follow_up_duration": {"type": "integer"},
        "disease_status_at_last_followup": {"type": "string"},
        "last_followup_date": {"type": "string"},  # ISO date format (yyyy-mm-dd) is recommended
        "cause_of_death": {"type": "string"},
        "tobacco_history": {"type": "string"},
        "alcohol_use": {"type": "string"},
    },
    "required": ["patient_last_name", "patient_first_name"],
}


if st.secrets["use_docker"] == "True" or check_password():

    if 'history' not in st.session_state:
         st.session_state.history = []

    if 'output_history' not in st.session_state:
         st.session_state.output_history = []

                
    if 'mcq_history' not in st.session_state:
         st.session_state.mcq_history = []

    # API_O = st.secrets["OPENAI_API_KEY"]
    # Define Streamlit app layout


    st.set_page_config(page_title='Oncology Parser Assistant', layout = 'centered', page_icon = ':stethoscope:', initial_sidebar_state = 'auto')
    st.title("📝 Oncology Parser Assistant")
    st.sidebar.markdown("### When finished trying various features, please    complete a [post-survey](https://nam04.safelinks.protection.outlook.com/?url=https%3A%2F%2Fnorthwestern.az1.qualtrics.com%2Fjfe%2Fform%2FSV_1WUkLabZFI8HdfE&data=05%7C02%7Cdavid.liebovitz%40nm.org%7C60ff56cac8584a3f2e8a08dc5507dbb0%7C2596038f3ea44f0caed1066eb6544c3b%7C0%7C0%7C638478739455911762%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C0%7C%7C%7C&sdata=iKpW%2BHxBIqlkCDhrjifFkPsyZWqkfUmXmKeVJ1nH6Gg%3D&reserved=0)! Thank you so much in advance!!")

    st.warning("""Who likes extra EHR clicks? What if AI could recognize all concepts and file them where they belong in the chart? This tool illustrates
                  progress in that direction with a variety of methods. Soon, one or more will meet muster for research or clinical use!""")
    disclaimer = """**Disclaimer:** This is a tool to assist chart abstraction for cancer related diagnoses. \n 
    2. This tool is not a real doctor. \n    
    3. You will not take any medical action based on the output of this tool. \n   
        """
    openai_api_key = fetch_api_key()
    openai.api_key = openai_api_key
    with st.expander('About Neurology Parser - Important Disclaimer'):
        st.write("Author: David Liebovitz, MD, Northwestern University")
        st.info(disclaimer)
        st.write("Last updated 3/17/24")
        selected_model = st.selectbox("Pick your GPT model:", ("GPT-3.5-turbo ($)","GPT-4 ($$$$)"))
        if selected_model == "GPT-3.5-turbo ($)":
            model = "gpt-3.5-turbo"
            st.session_state.model = model
        elif selected_model == "GPT-4 ($$$$)":
            model = "gpt-4-turbo-preview"
            st.session_state.model = model

 
    # st.info("📚 Let AI identify structured content from notes!" )
        

    schema_choice = st.sidebar.radio("Pick your extraction schema:", ("Schema 1", "Schema 2", "Schema 3", "Method 2: Consistent JSON"))
    # st.markdown('[Sample Oncology Notes](https://www.medicaltranscriptionsamplereports.com/hepatocellular-carcinoma-discharge-summary-sample/)')
    parse_prompt  = """You will be provided with unstructured text about a patient, and your task is to find all information related to any cancer 
    and reformat for quick understanding by readers. If data is available, complete all fields shown below. Leave blank otherwise.  extract cancer diagnosis date, any recurrence dates, all treatments given and current plan. 
    If there are multiple cancers, keep each cancer section distinct. Identify other medical conditions and include in a distinct section. 
    
    Fields to extract (return JSON):
    
    - Cancer type:
    
    - Cancer patient last name:
    
    - Cancer patient first name:
    
    - Cancer patient current age:
    
    - Cancer patient age at diagnosis:
    
    - Cancer patient sex:
    
    - Cancer diagnosis date:
    
    - Cancer past treatment:
    
    - Cancer current treatment:
    
    - Cancer current status details:
    
    - Cancer current status date:
    
    - Additional medical conditions:
    

    
    """

    # Set schemas for methods that require it.
        
    if schema_choice == "Complex Schema":
        schema = default_schema
        # st.sidebar.json(default_schema)    
    elif schema_choice == "Schema 1":
        schema = default_schema
        # st.sidebar.json(schema1)
    elif schema_choice == "Schema 2":
        schema = schema2
        # st.sidebar.json(schema2)
    elif schema_choice == "Schema 3":
        schema = schema3
        # st.sidebar.json(schema3)
    elif schema_choice == "Method 2: Consistent JSON":
        output_choice = "JSON"
    # # elif schema_choice == "Method 2":
    #     response = openai.ChatCompletion.create(
    #         model= selected_model,
    #         messages=[],
    #         temperature=0,
    #         top_p=1,
    #         frequency_penalty=0,
    #         presence_penalty=0
    #         )
        

    # def process_text(text, schema):
    #     llm = ChatOpenAI(temperature=0, model=model, verbose = True)


    
    if schema_choice != "Method 2":
      if schema_choice != "Method 2: Consistent JSON":
        llm = ChatOpenAI(temperature=0, model=model, verbose = True)
        chain = create_extraction_chain(schema, llm)
        
    # use_sample = st.checkbox("Use sample note")
    test_or_use =  st.radio("Generate a test note or enter your content. File(s) upload feature coming!", ("Generate a note", "Paste content"))
    
    if test_or_use == "Generate a note":
      
      oncology_diagnosis = st.text_input("Enter an oncologic diagnosis and any other details", placeholder = "e.g., 45F with breast cancer", key = 'oncology_diagnosis',)
      sample_prompt = f"{oncology_note} and here is the oncology diagnosis: {oncology_diagnosis}"
      if st.button("Generate a sample note"):
        prelim_note = answer_using_prefix(prefix, sample_prompt, sample_response, sample_prompt, temperature = 0.4, history_context = "", )
        st.session_state.copied_note = prelim_note
        st.write(st.session_state.copied_note)
  
    elif test_or_use == "Paste content":
      prelim_note = st.text_area("Paste your note here", height=600)
      st.session_state.copied_note = prelim_note
        
    if st.sidebar.button("Extract"):
        with st.expander("Click here to see the note you entered", expanded = True):
            st.write(st.session_state.copied_note)

        
        # if schema_choice != "Method 2":
        #     openai_api_key = fetch_api_key()
        #     extracted_data = chain.run(copied_note)
        #     with col2:
        #         st.markdown(extracted_data)
                
        if schema_choice == "Method 2: Consistent JSON":
            openai_api_key = fetch_api_key()
            st.write(st.session_state.copied_note)
            extracted_data = method3(st.session_state.copied_note, model, output_choice)
            # json_extract = extracted_data.json()
            st.sidebar.json(extracted_data)
        
        elif schema_choice == "Method 2":
            try:
                response= openai.ChatCompletion.create(
                model= model,
                messages=[
                    {"role": "system", "content": parse_prompt},
                    {"role": "user", "content": st.session_state.copied_note}
                ],
                temperature = 0, 
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
                )
                output = response.choices[0].message.content
                with st.sidebar:
                    st.json(output)
                    
            except:
                # st.write(f'Here is the error: {response}')
                st.write("OpenAI API key not found. Please enter your key in the sidebar.")
                st.stop()
        else:
            openai_api_key = fetch_api_key()
            extracted_data = chain.run(st.session_state.copied_note)
            with st.sidebar:
                st.sidebar.write(extracted_data)
  