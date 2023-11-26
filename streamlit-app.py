import streamlit as st
#from dynamodb_connection import DynamoDBConnection
import pandas as pd
import time
import boto3
import plotly.express as px


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

with placeholder.container():
      
    # Obtenemos los nuevos datos
    df_last = compute_movement()
    
    st.sidebar.markdown('## Seleccione los parametros de visualización')

    # create three columns
    row0_spacer1, kpi1, row0_spacer2, kpi2, row0_spacer3, kpi3 = st.columns((.5, 3, .1, 3, .1, 3))

    # fill in those three columns with respective metrics or KPIs 
    with kpi1:
        kpi1.metric(label="### Productividad Diaria", value="100%", delta=80)
    with kpi2:
        kpi2.metric(label="Productividad Semanal", value="100%", delta=-50)
    with kpi3:
        kpi3.metric(label="Productividad Mensual", value="100%", delta=10)
  
    # Reemplazamos el contenido del placeholder con la 
    #placeholder.line_chart(data=df_last, x='Date', y='Ratio', color=["#FF0000"], width=800, height=400, use_container_width=False)
    #placeholder.markdown("### Detailed Data View")
    #placeholder.dataframe(df_last)

    # create two columns for charts 
    row1_spacer1,fig_col1,row1_spacer2 = st.columns((.1, 10, .1,))
  
    with fig_col1:
        st.markdown("### First Chart")
        fig = px.line(data_frame=df_last, x='Date', y='Ratio',markers=True)
        fig.update_layout(height=800)
        #st.plotly_chart(fig,height=800)
        st.write(fig)
    st.markdown("### Detailed Data View")
    st.dataframe(df_last)
    time.sleep(1)   
    
