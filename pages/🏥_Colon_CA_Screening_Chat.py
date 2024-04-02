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


# Streamlit app
st.title("Reliable Content Chat Example")
with st.expander("ℹ️ About this App and Settings"):
    st.warning("Validate all responses - this is for exploration of AI at the NCCN meeting.")
    st.write("Author: David Liebovitz, MD")
    
with st.sidebar:
    model = st.selectbox("Select a model:", ["gpt-3.5-turbo", "gpt-4-turbo-preview"])

    # Reenable in order to create another vectorstore!    
    

# Get user input

st.warning("""This app leverages USPSTF content for an information basis. The purpose here is to illustrate grounding answers
           in reliable sources through Retrieval Augmented Generation (RAG). Processed content is stored in vector database and used when crafting a response. 
           The response will indicate if the reference material available fails to answer the question. """)

if st.secrets["use_docker"] == "True" or check_password2():
    topic = st.radio("Select a topic:", ["Colon Cancer Screening", "Pending - if time pre conference"], horizontal=True)
    if topic == "Colon Cancer Screening":
        vectorstore_label = "colon_ca.faiss"
        question_placeholder = "Why should a patient have a colon cancer screening?"
    elif topic == "Pending - if time pre conference":
        st.warning("Not implemented yet")
    st_callback = StreamlitCallbackHandler(st.container())
    with st.spinner("Preparing Databases..."):
        llm = ChatOpenAI(openai_api_key=st.secrets['OPENAI_API_KEY'], 
                         model_name =model, 
                         temperature=0.3,
                         streaming=True,
                )

        # Load the FAISS database
        if topic == "Colon Cancer Screening":
            model = "text-embedding-ada-002"
        elif topic == "ACP Suggested Content to Include in Referrals":
            model = "text-embedding-3-large"
        embeddings = OpenAIEmbeddings(openai_api_key=st.secrets['OPENAI_API_KEY'],model=model)
        vectorstore = FAISS.load_local(vectorstore_label, embeddings)

    # # Set up the OpenAI LLM
    # llm = OpenAI(temperature=0)

    # Create the question-answering chain
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever(), chain_type="stuff", callbacks=[st_callback],)

    user_role = st.radio("What is your role?", ["Patient", "Oncologist", "Other"], horizontal=True)
    if user_role == "Other":
        user_role = st.text_input("Enter your role:")

    query = st.text_input(f'Ask a question, e.g., "{question_placeholder}"',)

    final_query = f'{rag_prompt} As a {user_role}, so please use appropriate terms, {query}.'

    # If the user enters a query, get the answer
    if query:
        with st.spinner("Fomulating Answer..."):

            st.write(qa_chain(final_query)["result"])
            # st.write(answer["result"])