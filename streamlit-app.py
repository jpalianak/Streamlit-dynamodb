import streamlit as st
from dynamodb_connection import DynamoDBConnection

# Create a connection:
conn = st.experimental_connection("DynamoDBTable", type=DynamoDBConnection, api_type="pandas", table_name="DynamoDBTable")

# Get all items in the table:
st.write(conn.items())
