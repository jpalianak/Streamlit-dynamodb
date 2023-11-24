import streamlit as st
from dynamodb_connection import DynamoDBConnection
import pandas as pd
import time

# Crear el cliente de DynamoDB usando boto3
dynamodb = boto3.resource('DynamoDB', region_name='us-east-1')  # Reemplaza 'tu_region' con la región de tu tabla
table_name = 'DynamoDBTable'  # Reemplaza 'nombre_de_la_tabla' con el nombre de tu tabla en DynamoDB

# Obtener la tabla de DynamoDB
table = dynamodb.Table(table_name)

# Escanear toda la tabla
response = table.scan()
items = response['Items']

# Convertir los datos a un DataFrame de Pandas
df = pd.DataFrame(items)

# Mostrar el DataFrame
st.write(df)
