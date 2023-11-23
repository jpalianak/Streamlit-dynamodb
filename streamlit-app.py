import streamlit as st
from dynamodb_connection import DynamoDBConnection

# Create a connection:
conn = st.experimental_connection(
    "my_dynamodb_connection", type=DynamoDBConnection, api_type="pandas"
)

# Get all items in the table:
st.write(conn.items())
