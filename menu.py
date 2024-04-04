import streamlit as st

using_docker = "False"

def check_password():
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

def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("pages/main.py")
    st.sidebar.page_link("pages/⚖️_Bias_Detection.py")
    st.sidebar.page_link("pages/✔_Prior_Authorization_Help.py")
    st.sidebar.page_link("pages/👔_Interview_Practice.py")
    st.sidebar.page_link("pages/👩🏾‍💻_My_AI_Team.py")
    st.sidebar.page_link("pages/📝_Capture_Data_from_Notes.py")
    st.sidebar.page_link("pages/🗨️_Communication_and_DDx.py")
    st.sidebar.page_link("pages/🧠_Parkinson_Chat.py")
    if st.session_state.role in ["admin", "super-admin"]:
        st.sidebar.page_link("pages/admin.py", label="Manage users")
        st.sidebar.page_link(
            "pages/super-admin.py",
            label="Manage admin access",
            disabled=st.session_state.role != "super-admin",
        )


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("login.py", label="Log in")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "role" not in st.session_state or st.session_state.role is None or check_password() is False:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "role" not in st.session_state or st.session_state.role is None or check_password() is False:
        st.switch_page("login.py")
    menu()