    # Import necessary libraries

import os  # Used for accessing environment variables like our secret OpenAI API key.
from openai import OpenAI
import openai  # Import the OpenAI library to interact with the API
import streamlit as st  # Streamlit library for creating web apps
from datetime import date
import json
import markdown2

#set default name and info, don't have them enter it 
# don't need session state- done
# could potentially download pdf (option), or can look at easy copy and pasting of an output
# start with default values for patients and physician, with option to edit. Put default values for st.text_input (could use random numbers and have chatgpt
# generate list of random names, populate it with random name)
# use tabs in streamlit instead of sidebar
# get templates from doximity
# could make chatbot with advice for practice administrators. Standard chatbot (chatting with chatgpt), teaching aids git hub has updated one in David's git hub
# could you pull over teaching aids on to that? Maybe forget teaching aids b/c it uses sidebar (want to avoid). Code built in system prompt- practice administrator help
# Can go back and forth and get answer you like and formatting you like, then include that in system prompt so that it knows how to format it 

#Put pretend data for phyisician defaults (hid it), dont let them change it
#let them fill out patient stuff, don't put real patient information 
#add edit patient letter/tweak, make conversational

##ctrl c to stop
# Load your OpenAI API key from secrets.toml
api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = api_key

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=api_key)

st.set_page_config(page_title="Prior Authorization Help", page_icon="✔")
def ChatGPT(messages):
    # Ensure messages is a list
    if not isinstance(messages, list):
        messages = [messages]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

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
        if st.secrets["use_docker"] == "False":
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

st.title("✔ Prior Authorization Help")
st.warning("""This is for educational purposes only, please do not input real patient information or use in clinical practice. For the 
          purposes of the AAN, please try this out with scenarios you have encountered that need prior authorization, and don't forget to provide feedback!""")

if check_password2() or st.secrets["use_docker"] == "True":
    # Use st.radio to create tabs
    #page = st.radio("Go to:", ["Chat with chatGPT", "Prior authorization help"])

    # Initialize response in session_state if not already present

    # Initialize response in session_state if not already present

    if 'chat_hx' not in st.session_state:
        st.session_state.chat_hx =  {}
    if 'response' not in st.session_state:
        st.session_state["response"] = []
    if "messages" not in st.session_state: 
        system_context_friend = "You are a helpful nurse with medical knowledge helping a physician compose a prior authorization to obtain insurance approval for a medication or procedure"
        st.session_state["messages"] = [{"role": "system", "content": system_context_friend}]

    # Default physician details
    physician_name = "Dr. Jane Doe"
    physician_phone = "123-456-7890"
    physician_fax = "123-456-7891"
    physician_npi = "1234567890"
    physician_address = "1234 Health St, Wellness City, HC 12345"

    today = date.today()

    st.title('Patient Details')
    patient_name = st.text_input("Enter patient's name", value="Jane Smith")
    patient_dob = st.text_input("Enter patient's date of birth", value="01/01/1950")
    med_pa = st.text_input("Enter medication or procedure you are trying to get a prior authorization for", value="axicabtagene ciloleucel")
    diagnosis = st.text_input("Enter patient's diagnosis", value="DLBCL")
    extra_info = st.text_area("Enter any additional information you would like included in the letter here (optional)", value = "The patient with diffuse large B-cell lymphoma (DLBCL) has undergone and failed to respond to two or more lines of systemic therapy, including high-dose chemotherapy and autologous stem cell transplant.")
    if st.button("Compose Initial Prior Authorization"):
        template_medication = f"""

            {today}

            To Whom It May Concern,

            I am writing to request authorization for Yescarta (axicabtagene ciloleucel) for my patient, {patient_name}, diagnosed with diffuse large B-cell lymphoma (DLBCL).

            Physician's Information:
            Name: {physician_name}
            Phone: {physician_phone}
            Fax: {physician_fax}
            NPI: {physician_npi}
            Address: {physician_address}

            Patient's Information:
            Name: {patient_name}
            DOB: {patient_dob}

            Based on the patient's condition and having failed two or more lines of systemic therapy, we believe the patient meets all necessary criteria for Yescarta.

            Drug Criteria Requirements Met:
            - Patient has been diagnosed with relapsed or refractory large B-cell lymphoma, including DLBCL, after two or more lines of systemic therapy.
            - Patient has a performance status that supports the feasibility of undergoing the CAR T-cell therapy treatment process.
            - Patient has adequate organ function as required for Yescarta therapy.
            - Patient has been informed of the potential benefits and risks of Yescarta therapy, including the risk of cytokine release syndrome (CRS) and neurologic toxicities, and wishes to proceed.

            Please consider this letter as a formal request for the prior authorization of Yescarta. Attached are all necessary medical records, including prior treatment history and documentation supporting this request.

            Thank you for your attention to this matter.

            Sincerely,

            {physician_name}
            """

        
        template_procedure = f"""
    To Whom It May Concern,
            I am writing to request authorization for a PET/CT scan for my patient, {patient_name}, diagnosed with {diagnosis}. 

            Physician's Information:
            Name: {physician_name}
            Phone: {physician_phone}
            Fax: {physician_fax}
            NPI: {physician_npi}
            Address: {physician_address}

            Patient's Information:
            Name: {patient_name}
            DOB: {patient_dob}

            A PET/CT scan is medically necessary to assess the extent of disease, evaluate treatment response, and guide further management in this patient with diffuse large B-cell lymphoma (DLBCL). Given the patient's history of relapsed or refractory DLBCL after two or more lines of systemic therapy, accurate staging and assessment through PET/CT are critical to optimizing the treatment approach, including consideration for targeted therapies such as CAR T-cell therapy.

            Sincerely,
            {physician_name}
"""


        user_query = {"role": "system", "content": f"""Generate a prior authorization letter for either a medication or a procedure: {med_pa}  If {med_pa} is a medication, 
                generate a medication prior authorization letter, if {med_pa} is a procedure, generate a procedure prior authorization letter. For a medication use the following templated (with the current request, {med_pa}): {template_medication}. 
                The strucutre is an example for the drug Lecanemab, if a separate drug is requested please fill out the template appropriately with that drug's requirements. 
                Please include the drug requirements in a wording that is approrpriate for a doctor sending a letter to an insurance company about their patient. Please assume the patient has 
                met all the requirements for the drug. For a procedure please use the following strucutre : {template_procedure}, again for the current reequest, {med_pa}. The wording will need to change depending on the diagnosis and procedure requested. Please include procedure requirements that are approrpriate for that specific procedure requested ({med_pa}) 
                Please assume the patient qualifies for the procedure. For either type of letter (one for a medication or one for a procedure) replace today's date with the actual date of today. Include blanks for additional details to be provided by the user if not given. Please include {extra_info} if provided in the letter where approrpriate, 
                """}
        
        st.session_state.messages.append(user_query)
        response_text = ChatGPT(user_query)
        #st.session_state.chat_hx[user_query] = response_text
        st.session_state.messages.append({"role": "assistant", "content":response_text})
        st.session_state.response.append(response_text)

    st.title("Edit the prior authorization")
    changes = st.text_area("What would you like to change about the letter?")

    # Display the current inputs
    #st.subheader("Current Patient Details")
    #st.write(f"**Name:** {patient_name}")
    #st.write(f"**Date of Birth:** {patient_dob}")
    #st.write(f"**Medication or Procedure needing a prior authorization:** {med_pa}")
    #st.write(f"**Patient Diagnosis:** {diagnosis}")
    #st.write(f"**Additional Information:** {extra_info}")


    # Update your session state to include the new message for future reference

    if st.button("Edit letter"):
        new_message = {"role": "system", "content": f"""Please edit the prior authorization with these requested edits: {changes}"""}
        st.session_state["messages"].append(new_message)
        response_text = ChatGPT(st.session_state["messages"]) 
        st.session_state["messages"].append({"role": "system", "content": response_text})
        st.session_state.response.append(response_text)
        #st.write(response_text)

    if st.session_state.response:
        st.subheader("Current Letter")
        letter = st.session_state.response[-1]
        st.write(letter)
        html = markdown2.markdown(letter,  extras=["tables"])
        st.download_button('Download Current Letter', html, f'letter_draft.html', 'text/html')