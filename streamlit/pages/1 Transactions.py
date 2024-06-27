from collections import defaultdict
import streamlit as st
import requests
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import datetime
import json

api_url_create_transaction = "http://127.0.0.1:8000/transaction/create"
api_url_get_transactions = "http://127.0.0.1:8000/transaction/get"
st.set_page_config(
    page_title="Transactions",
    page_icon="",
    layout="wide"
)
st.set_option('deprecation.showPyplotGlobalUse', False)
month_to_number = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}
def request_data(email: str, month: int, year: int):
    month_number = month_to_number.get(month, 0)
    if month_number == 0:
        raise ValueError("Invalid month name")
    payload = {
        "email": email,
        "month": month_number,
        "year": year
    }
    response = requests.post(api_url_get_transactions, json=payload)
    if response.status_code == 200:
        return response.json()
    return None

def prepare_data(response_data):
    try:
        data = json.loads(response_data)
        if isinstance(data, list):
            prepared_data = []
            for item in data:
                if isinstance(item, dict):
                        prepared_item = {
                            "type": item.get("type"),
                            "category": item.get("category"),
                            "amount": item.get("amount"),
                            "date": item.get("date")
                        }
                        prepared_data.append(prepared_item)
                else:
                    print(f"Item {item} is not a dictionary")
            return prepared_data
        else:
            print("Response data is not a list")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")

# Функція для підрахунку категорій
def calculate_category_sums(prepared_data):
    category_sums_income = defaultdict(float)
    category_sums_expense = defaultdict(float)

    for item in prepared_data:
        amount = item.get("amount", 0.0)
        category = item.get("category", "Others")
        trans_type = item.get("type")

        if trans_type == "Income":
            category_sums_income[category] += amount
        elif trans_type == "Expanse":
            category_sums_expense[category] += amount
    print(category_sums_expense)
    return category_sums_income, category_sums_expense

def plot_pie_chart(data, title):
    categories = list(data.keys())
    amounts = list(data.values())

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    ax.set_title(title)
    st.pyplot(fig)

st.header("Greetings!")
st.subheader("Your transactions :credit_card:")
st.markdown("---")

maincol1, maincol2 = st.columns(2)
with maincol2:
    st.write("Adding new transaction:")
    con1=st.container(border = True)
    with con1:
        transaction_type = st.selectbox("Type", options = ("Income", "Expanse", "Saving"))
        with st.form("Transaction"):
            col1,col2,col3,col4 = st.columns(4)
            number = col1.text_input("Number")
            if transaction_type == "Income":
                category = col2.selectbox("Category", options =("Salary", "Commerce", "Bonus", "Credit", "Saving"))
            elif transaction_type == "Expanse":
                category = col2.selectbox("Category", options = ("Food",
                     "Hospitality", "Alcohol","Tobacco","Clothing",
                     "Public_utilities","Medical","Transport","Communication",
                     "Education","Others","Special","Gardening"))
            elif transaction_type == "Saving":
                category = col2.selectbox("Category", options =("Saving", ))
            date = col3.date_input("Date").isoformat()
            
            s_state = col4.form_submit_button("Submit")
            if s_state:
                if number == "" or category == "" or date == "":
                    st.warning("Please fill blank fields")
                else:
                    transaction_data = {
                        "email": st.session_state['user_id'],
                        "type": transaction_type,
                        "amount": float(number),
                        "category": category,
                        "date": date,
                    }
                    response = requests.post(api_url_create_transaction, json=transaction_data)
                    if response.status_code == 200:
                        st.success("Submitted succesfully")


def get_month_list():
    return [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
with maincol1:
    i = 0
    current_year = datetime.datetime.now().year
    years = [str(year) for year in range(current_year - 4, current_year + 1)]


    selected_year = st.selectbox("Choose year", years)
    selected_month = st.selectbox("Choose month", get_month_list())
 
    st.write(f"Your transactions in {selected_month} {selected_year}:")
    response_data = request_data(st.session_state['user_id'], selected_month, selected_year)
    prepared_data = prepare_data(response_data)
    if response_data:
        df = pd.DataFrame(prepared_data)
        st.dataframe(df, width=800)
    else:
        st.error("Failed to fetch transactions.")




st.markdown("---")
st.markdown("Your staticstics of Income and expenses")
income_data, expense_data = calculate_category_sums(prepared_data)
col1, col2 = st.columns(2)

with col1:
    
    st.subheader("Income Distribution")
    fig_income = plot_pie_chart(income_data, "Income Distribution for " + selected_month)

with col2:
    st.subheader("Expense Distribution")
    fig_expense = plot_pie_chart(expense_data, "Expense Distribution for " + selected_month)