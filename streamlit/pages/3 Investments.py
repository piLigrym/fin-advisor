import streamlit as st 
import pandas as pd 
from matplotlib import pyplot as plt 
import numpy as np 
import requests

st.set_page_config( 
    page_title="Investments", 
    page_icon="", 
    layout="centered" 
) 
 
def min_inv(email):
    try: 
        response = requests.post("http://127.0.0.1:8000/predictions/predict-recommend-invest", json={"email": email}) 
        prediction = response.json()["prediction"]
        return prediction
    except Exception as e:
            return str(e)
 
st.header("Recommended investments :chart_with_upwards_trend:") 
st.subheader("Based on your financial activity over the last *30 days*, I suggest the following investments:") 

try:
    predicted_value = min_inv(st.session_state['user_id'])
    st.metric("*Your recommended investition is:*", value=predicted_value)
except TypeError as te:
    st.error(f"TypeError occurred: {te}")
except Exception as e:
    st.error(f"Exception occurred: {str(e)}")

st.subheader("Best companies to invest now:")
response = requests.get("http://127.0.0.1:8000/predictions/predict-profitable-stocks")
if response.status_code == 200:
    profitable_stocks = response.json()["profitable_stocks"]
    for index, item in enumerate(profitable_stocks):
        st.subheader(f"{index + 1}: {item['Company Name']}")
        st.write(f"Current Price: ${item['Current Price']:.2f}")
        st.write(f"Profit per Share: ${item['Profit per Share']:.2f}")
        st.write(f"Profit to Price Ratio for Next 30 Days: ${item['Profit to Price Ratio']:.2f}")
        st.write("Predictable possible profit for Next 30 Days:")
        st.subheader(f" {(item['Profit to Price Ratio'] + 1) * predicted_value:.2f} Hryvnas")
        st.markdown("---")  # Додати роздільник між компаніями
else:
    st.error("Failed to fetch profitable stocks prediction")
    
st.subheader("Here is some tips to upgrade your financial literacy:") 
# st.image("smart.jpg", "Recommendations")