from json import JSONDecodeError
import streamlit as st
import pandas as pd
import requests
import logging


st.set_page_config(
    page_title="Main",
    page_icon="", 
    layout="centered",
    initial_sidebar_state="expanded"
)
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
def register_user(f_name, l_name, email, password):
    url = "http://localhost:8000/users/register"
    payload = {
        "first_name": f_name,
        "last_name": l_name,
        "email": email,
        "password": password
        }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        st.success("Registration successful")
    else:
        st.error("Registration failed")
def login_user(email, password):
    url = "http://localhost:8000/users/login"
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        try:
            data = response.json()
            access_token = data.get('access_token')
            print(data)
            if access_token:
                user_id = data.get('user', {}).get('email')
                print(user_id)
                st.success("Login successful")
                st.write(f"Welcome, {data['user']['first_name']}!")
                return user_id
            else:
                st.error("Login failed: No access token received")
        except JSONDecodeError:
            st.error("Login failed: Invalid response format")
    elif response.status_code == 401:
        st.error("Login failed: Incorrect email or password")
    else:
        st.error(f"Login failed: Unexpected error ({response.status_code})")

logging.basicConfig(level=logging.DEBUG) 

st.title("Hello there!")
st.subheader("I'm an app for analyzing expenses and managing your money :moneybag:")
st.subheader("Also, I will be able to help you decide where to invest your savings to get a profit :dollar:")
st.markdown("---")

if st.session_state['user_id'] == None:
    option = st.radio("Choose action", ("Register", "Login"))
    if option == "Register":
        st.markdown("**To use me you should get through *short* registration form**")
        st.markdown("# Registration")
        with st.form("Reg form"):
            col1,col2 = st.columns(2)
            f_name = col1.text_input("First Name")
            l_name = col2.text_input("Last Name")
            email = st.text_input("Email adress")
            password = st.text_input("Password")
            conf_pas = st.text_input("Confirm password")
            s_state = st.form_submit_button("Register")
            if s_state:
                if f_name == "" or l_name == "" or email == "" or password == "" or conf_pas == "":
                    st.warning("Please, fill blank fields")
                else:
                    if password != conf_pas:
                        st.warning("Confirmation password is incorrects")
                    else: 
                        register_user(f_name, l_name, email, password)
                    
    elif option == "Login":                
        st.markdown("# Login")
        with st.form("Log form"):
            email = st.text_input("Email adress")
            password = st.text_input("Password")
            s_state = st.form_submit_button("Login")
            if s_state:
                if email == "" or password == "":
                    st.warning("Please, fill blank fields")
                else:
                    user_id = login_user(email, password)
                    print(user_id)
                    if user_id:
                        st.session_state['user_id'] = user_id
                        st.success("Login successful")
                        st.write(f"User ID: {user_id}")
                        st.switch_page("pages/1 Transactions.py")
                    else:
                        st.error("Login failed. Please check your credentials.")
else:
    st.success("You are logged in as: " + st.session_state['user_id'])
