import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import datetime
import json
import requests


st.set_page_config(
    page_title="Transactions",
    page_icon="",
    layout="centered"
)
api_url_get_budgets = "http://127.0.0.1:8000/budget/get"
api_url_create_budget = "http://127.0.0.1:8000/budget/create"

st.markdown("""
<style>
.st-emotion-cache-keje6w 
    {
            
    }
</style>      
""",unsafe_allow_html = True,)
st.header("Your budgets :briefcase:")
st.markdown("---")

def get_user_budgets(email, month, year):
    payload = {
        "email": email,
        "month": month,
        "year": year
    }
    try:
        response = requests.post(api_url_get_budgets, json=payload)
        if response.status_code == 200:
            data = prepare_data(response.json())
            if isinstance(data, list):  # Перевірка чи data - це список об'єктів
                df = pd.DataFrame(data)
                st.write(df)
            else:
                st.error(f"Failed to retrieve budgets. Unexpected data format.")
        else:
            st.error(f"Failed to retrieve budgets. Status code: {response.status_code}")
    except requests.RequestException as e:
        st.error(f"Failed to connect to API: {str(e)}")

def prepare_data(response_data):
    try:
        data = json.loads(response_data)
        if isinstance(data, list):
            prepared_data = []
            for item in data:
                if isinstance(item, dict):
                        prepared_item = {
                            "total_budget": item.get("total_budget"),
                            "food": item.get("food"),
                            "hospitality": item.get("hospitality"),
                            "alcohol": item.get("alcohol"),
                            "tobacco": item.get("tobacco"),
                            "clothing": item.get("clothing"),
                            "public_utilities": item.get("public_utilities"),
                            "medical": item.get("medical"),
                            "transport": item.get("transport"),
                            "communication": item.get("communication"),
                            "education": item.get("education"),
                            "others": item.get("others"),
                            "special": item.get("special"),
                            "gardening": item.get("gardening"),
                            "saving": item.get("saving"),
                        }
                        print(prepared_item)
                        prepared_data.append(prepared_item)
                else:
                    print(f"Item {item} is not a dictionary")
            return prepared_data
        else:
            print("Response data is not a list")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")

def get_month_list():
    return [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

month_to_number = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}
current_year = datetime.datetime.now().year
years = [str(year) for year in range(current_year - 4, current_year + 1)]


selected_year = st.selectbox("Choose year", years)
selected_month = st.selectbox("Choose month", get_month_list())
month_number = month_to_number.get(selected_month, 0)
option = st.radio("Choose action", ("Create Budget", "View Budget"))
if option == "Create Budget":
    with st.form("budgets_form", border = True):
        Total_Budget = st.number_input("Prefered budget for month:", min_value = 500, max_value = 1000000, step = 500)
        col1, col2 = st.columns(2)
        with col1:
            Food=st.number_input("Food", min_value = 0, step = 100, value = 0)
            Alcohol=st.number_input("Alcohol", min_value = 0, step = 100, value = 0)
            Clothing=st.number_input("Clothing", min_value = 0, step = 100, value = 0)
            Medical=st.number_input("Medical", min_value = 0, step = 100, value = 0)
            Communication=st.number_input("Communication", min_value = 0, step = 100, value = 0)
            Others=st.number_input("Others", min_value = 0, step = 100, value = 0)
            Gardening=st.number_input("Gardening", min_value = 0, step = 100, value = 0)
        with col2:
            Hospitality=st.number_input("Hospitality", min_value = 0, step = 100, value = 0)
            Tobacco=st.number_input("Tobacco", min_value = 0, step = 100, value = 0)
            Public_utilities=st.number_input("Public_utilities", min_value = 0, step = 100, value = 0)
            Transport=st.number_input("Transport", min_value = 0, step = 100, value = 0)
            Education=st.number_input("Education", min_value = 0, step = 100, value = 0)
            Special=st.number_input("Special", min_value = 0, step = 100, value = 0)
            Saving = st.number_input("Saving", min_value = 0, step = 100, value = 0)
        st.markdown("---")
        s_state = st.form_submit_button("Save")
        if s_state:
            if Total_Budget == "":
                st.warning("Please fill blank fields")
            else:
                budget_data = {
                    "email": st.session_state['user_id'],
                    "total_budget": float(Total_Budget),
                    "food": float(Food),
                    "hospitality": float(Hospitality),
                    "alcohol": float(Alcohol),
                    "tobacco": float(Tobacco),
                    "clothing": float(Clothing),
                    "public_utilities": float(Public_utilities),
                    "medical": float(Medical),
                    "transport": float(Transport),
                    "communication": float(Communication),
                    "education": float(Education),
                    "others": float(Others),
                    "special": float(Special),
                    "gardening": float(Gardening),
                    "saving": float(Saving),
                    "month": month_number,
                    "year": selected_year
                }
                response = requests.post(api_url_create_budget, json=budget_data)
                if response.status_code == 200:
                    st.success("Submitted succesfully")
elif option == "View Budget":
    st.write(f"Your budgets in {selected_month} {selected_year}:")
    month_number = month_to_number.get(selected_month, 0)
    if month_number == 0:
        raise ValueError("Invalid month name")
    get_user_budgets(st.session_state['user_id'], month_number, selected_year)

    

        
