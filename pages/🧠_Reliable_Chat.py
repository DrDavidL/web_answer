import streamlit as st
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
# from langchain.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
# from langchain.chat_models import ChatOpenAI
# from langchain.chains import VectorDBQA
from langchain.chains import RetrievalQA
# from langchain.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from prompts import rag_prompt, references_used
from langchain.callbacks.streamlit import StreamlitCallbackHandler

st.set_page_config(page_title='Neurology Chats', layout = 'centered', page_icon = "💬", initial_sidebar_state = 'auto')    
st.sidebar.markdown("### When finished testing - please complete the [post-survey](https://northwestern.az1.qualtrics.com/jfe/form/SV_09hfbEnz1uSW4rY) to help us improve this tool!")

def check_password2():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"] or st.session_state["password"] == st.secrets["password2"]:
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
            st.write("*Visit the AAN Practice & Policy Hub Booth to obtain passcodes*")
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


# Streamlit app
st.title("Reliable Content Chat Example")
with st.expander("ℹ️ About this App and Settings"):
    st.warning("Validate all responses - this is for exploration of AI at the AAN meeting.")
    st.write("Author: David Liebovitz, MD")
    

    

# Get user input

st.warning("""This demo is designed to retrieve responses from pre-processed sources (shown on the left) using a Retrieval Augmented Generation (RAG) technique .  The app uses sources related to Parkinson’s disease and ACP guidelines for referrals to neurology.  Your questions should be related to these topics.   """)

if st.secrets["use_docker"] == "True" or check_password2():
    with st.sidebar:
        model = st.selectbox("Select a model:", ["gpt-3.5-turbo", "gpt-4-turbo-preview"], index=0)
    topic = st.radio("Select a topic:", ["Parkinson's Disease", "ACP Suggested Content to Include in Referrals"], horizontal=True)
    if topic == "Parkinson's Disease":
        vectorstore_label = "parkinson_disease.faiss"
        question_placeholder = "What are the symptoms of Parkinson's disease?"
        with st.sidebar:
            with st.expander("Parkinson's Disease Sources"):
                st.markdown(references_used)
    elif topic == "ACP Suggested Content to Include in Referrals":
        # st.sidebar.markdown("[ACP Referral Guidelines](https://www.acponline.org/clinical-information/high-value-care/resources-for-clinicians/high-value-care-coordination-hvcc-toolkit/pertinent-data-sets)")
        st.sidebar.info("""*Description:*  \n American College of Physicians High Value Care Coordination Project –  \n\n The AAN developed Pertinent Data Sets for information PCP’s should include or consider for most common reasons for neurology referrals.
                        [ACP Referral Guidelines](https://www.acponline.org/clinical-information/high-value-care/resources-for-clinicians/high-value-care-coordination-hvcc-toolkit/pertinent-data-sets)
""")
        vectorstore_label = "neuro_assess.faiss"
        question_placeholder = "What content should be included in a referral for headache?"
    st_callback = StreamlitCallbackHandler(st.container())
    with st.spinner("Preparing Databases..."):
        llm = ChatOpenAI(openai_api_key=st.secrets['OPENAI_API_KEY'], 
                         model_name =model, 
                         temperature=0.3,
                         streaming=True,
                )

        # Load the FAISS database
        embeddings = OpenAIEmbeddings(openai_api_key=st.secrets['OPENAI_API_KEY'],model="text-embedding-3-large")
        vectorstore = FAISS.load_local(vectorstore_label, embeddings)

    # # Set up the OpenAI LLM
    # llm = OpenAI(temperature=0)

    # Create the question-answering chain
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever(), chain_type="stuff", callbacks=[st_callback],)

    user_role = st.radio("What is your role?", ["Patient", "Neurologist", "Other"], horizontal=True)
    if user_role == "Other":
        user_role = st.text_input("Enter your role:")

    query = st.text_input(f"Ask a question, e.g., {question_placeholder}",)

    final_query = f'Updated System Prompt: {rag_prompt}, User role (use appropriate terminology to the user):{user_role}, question: {query}.'

    # If the user enters a query, get the answer
    if query:
        with st.spinner("Fomulating Answer..."):
            st.info("GPT-3.5 is faster; GPT-4 is slower at the moment yet more accurate and comprehensive. Response time here will improve. Switch models on the left sidebar.")
            st.write(qa_chain(final_query)["result"])
            # st.write(answer["result"])