import streamlit as st
import pandas as pd
import time
import boto3
import plotly.express as px
import datetime


st.set_page_config(layout="wide")

# Creamos un placeholder inicial vacío
placeholder = st.empty()

def get_data():
  # Crear el cliente de DynamoDB usando boto3
  dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Reemplaza 'tu_region' con la región de tu tabla
  table_name = 'DynamoDBTable'  # Reemplaza 'nombre_de_la_tabla' con el nombre de tu tabla en DynamoDB

  # Obtener la tabla de DynamoDB
  table = dynamodb.Table(table_name)

  # Escanear toda la tabla
  response = table.scan()
  items = response['Items']

  # Convertir los datos a un DataFrame de Pandas
  df = pd.DataFrame(items)
  df['Date_num'] = pd.to_datetime(df['Date']).astype('int64') // 10**9
  df = df.sort_values(by='Date_num')
  return df
  
def compute_movement(df_orig,maquina,d_ini,d_fin): 

  # Calculo del centro del bounding box
  df_orig['Xcenter'] = df_orig['Xmax'] - df_orig['Xmin']
  df_orig['Ycenter'] = df_orig['Ymax'] - df_orig['Ymin']
   
  # Filtro del dataframe segun los parametros seleccionados
  df_filter = df_orig[(pd.to_datetime(df_orig['Date']).dt.date >= d_ini) & (pd.to_datetime(df_orig['Date']).dt.date <= d_fin)]

  # Crear un nuevo dataframe
  df_new = pd.DataFrame()

  # Calculo de la diferencia de tiempo entre registro
  df_new['Date'] = df_filter['Date'].iloc[1:]
  df_new['Date_diff'] = df_filter['Date_num'] - df_filter['Date_num'].shift()

  # Calculo de la diferencia en X e Y de los centros de cada registro
  xcenter_diff = abs(df_filter['Xcenter'] -
                     df_filter['Xcenter'].shift()).iloc[1:]
  ycenter_diff = abs(df_filter['Ycenter'] -
                     df_filter['Ycenter'].shift()).iloc[1:]

  # umbral de diferencia de posicion del centro del bounding box para determinar si esta en movimieno o no
  threshold = 0.001
  
  # Deteminar movimiento o no. Si la diferencia en X o en Y es mayor al threshold se esta moviendo, si es menor esta detenida.
  df_new['Movement'] = ['SI' if x > threshold or y >
                        threshold else 'NO' for x, y in zip(xcenter_diff, ycenter_diff)]

  # Mascara de los registros que tienen SI en movimiento.
  si_mask = (df_new['Movement'] == 'SI').astype(int).tolist()

  # Nueva columna con cero donde el movimiento es NO y Date_diff donde el movimiento es SI.
  df_new['Date_diff_aux'] = [delta * mask if mask else 0 for delta,
                             mask in zip(df_new['Date_diff'], si_mask)]

  # Acumulado de tiempo de los registros con movimiento SI
  df_new['Cumulative_sum_si'] = df_new['Date_diff_aux'].cumsum()

  # Acumulado de tiempo total
  df_new['Cumulative_total'] = df_new['Date_diff'].cumsum()

  # Porcentaje de productividad
  df_new['Ratio'] = df_new['Cumulative_sum_si'] / df_new['Cumulative_total']
  return df_new

# Obtenemos los datos
df_orig = get_data()
  
Maq1, Maq2, Maq3 = st.tabs(["Maquina 1", "Maquina 2", "Maquina 3"])

with Maq1:
  st.write('')
  row0_spacer1, col1, row0_spacer2, col2, row0_spacer3, col3 = st.columns((.7, 3, .1, 3, .1, 3))
  with col1
    st.metric(label="### Productividad Diaria", value="100%", delta=80)
  with col2
    st.metric(label="### Productividad Semanal", value="100%", delta=80)
  with col3
    st.metric(label="### Productividad Mensual", value="100%", delta=80)
       
time.sleep(1)   
    
