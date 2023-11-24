import streamlit as st
from dynamodb_connection import DynamoDBConnection
import pandas as pd
import time

# Creamos un placeholder inicial vacío
placeholder = st.empty()

def get_data():
  conn = st.connection("DynamoDBTable", type=DynamoDBConnection, api_type="pandas", table_name="DynamoDBTable")
  df = conn
  df['Date_num'] = pd.to_datetime(df['Date']).astype('int64') // 10**9
  return df

def compute_movement(): 
  df_orig = get_data()
  df_orig['Xcenter'] = df_orig['Xmax'] - df_orig['Xmin']
  df_orig['Ycenter'] = df_orig['Ymax'] - df_orig['Ymin']

  df_new = pd.DataFrame()

  df_new['Date'] = df_orig['Date'].iloc[1:]
  df_new['Date_diff'] = df_orig['Date_num'] - df_orig['Date_num'].shift()

  threshold = 0.001
  xcenter_diff = abs(df_orig['Xcenter'] -
                     df_orig['Xcenter'].shift()).iloc[1:]
  ycenter_diff = abs(df_orig['Ycenter'] -
                     df_orig['Ycenter'].shift()).iloc[1:]

  df_new['Movement'] = ['SI' if x > threshold or y >
                        threshold else 'NO' for x, y in zip(xcenter_diff, ycenter_diff)]

  si_mask = (df_new['Movement'] == 'SI').astype(int).tolist()
  df_new['Date_diff_aux'] = [delta * mask if mask else 0 for delta,
                             mask in zip(df_new['Date_diff'], si_mask)]
  df_new['Cumulative_sum_si'] = df_new['Date_diff_aux'].cumsum()
  df_new['Cumulative_total'] = df_new['Date_diff'].cumsum()
  df_new['Ratio'] = df_new['Cumulative_sum_si'] / df_new['Cumulative_total']
  return df_new

while True:
    # Obtenemos los nuevos datos
    df_last = compute_movement()

    # Reemplazamos el contenido del placeholder con la 
    placeholder.line_chart(data=df_last, x='Date', y='Ratio', color=["#FF0000"], width=800, height=600, use_container_width=False)
  
    # Actualizamos cada 1 minutos
    time.sleep(60)
