import streamlit as st
import pandas as pd
import time
import boto3
import plotly.express as px
import datetime

st.set_page_config(layout="wide")

# Creamos un placeholder inicial vacío
placeholder = st.empty()

# Header  
#st.header(r"$\small \color{black} \textbf{Productivity Dashboard}$")
#st.write('')

# Footer
footer="""<style>
a:link , a:visited{color: blue;background-color: transparent;text-decoration: underline;}
a:hover,  a:active {color: red;background-color: transparent;text-decoration: underline;}
.footer {position: fixed;left: 0;bottom: 0;width: 100%;background-color: white;color: black;text-align: center;}
</style>
<div class="footer">
<p>Developed by AIRBIZ <a style='display: block; text-align: center;' href="https://www.airbiz.com/" target="_blank">www.airbiz.com</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

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
  df_new['Ratio'] = df_new['Ratio']*100
  return df_new

def line_graphic_maq(df_orig,maq,d_ini,d_fin): 
  df_last = compute_movement(df_orig,maq,d_ini,d_fin)
  fig = px.line(data_frame=df_last, x='Date', y='Ratio',markers=True)
  fig.update_layout(xaxis_title="Date", yaxis_title="Productivity [%]",width=550,height=350)
  fig.update_yaxes(range=[0, 100]) 
  return fig

def line_graphic_main(df_orig,maq,d_ini,d_fin): 
  df_last = compute_movement(df_orig,maq,d_ini,d_fin)
  fig = px.line(data_frame=df_last, x='Date', y='Ratio',markers=True)
  fig.update_layout(xaxis_title="Date", yaxis_title="Daily productivity [%]",width=550,height=350)
  fig.update_yaxes(range=[0, 100]) 
  return fig
  
# Obtenemos los datos
df_orig = get_data()

# Obtener la fecha actual
hoy = datetime.date.today()

# Calcular el día de la semana actual (0 es lunes, 6 es domingo)
dia_semana_actual = hoy.weekday()

# Calcular el desplazamiento necesario para llegar al lunes (inicio de semana laboral)
inicio_semana_laboral = hoy - datetime.timedelta(days=dia_semana_actual)

# Calcular el desplazamiento necesario para llegar al viernes (final de semana laboral)
fin_semana_laboral = hoy + datetime.timedelta(days=(4 - dia_semana_actual))

# Obtener el primer día del mes actual
inicio_mes = hoy.replace(day=1)

# Obtener el último día del mes actual
if hoy.month == 12:  # Si el mes actual es diciembre
    siguiente_mes = inicio_mes.replace(year=inicio_mes.year + 1, month=1)
else:
    siguiente_mes = inicio_mes.replace(month=inicio_mes.month + 1)
fin_mes = siguiente_mes - datetime.timedelta(days=1)

Main, Maq1, Maq2, Maq3, Maq4, Maq5, Maq6 = st.tabs(["Main", "Maquina 1", "Maquina 2", "Maquina 3", "Maquina 4", "Maquina 5", "Maquina 6"])

with Main:
  row1_col1, row1_col2, row1_col3 = st.columns(3)
  with row1_col1:
    d_ini = pd.to_datetime(hoy).date()
    d_fin = pd.to_datetime(hoy).date()
    fig = line_graphic_main(df_orig,"maq1",d_ini,d_fin)
    fig.update_layout(yaxis_title="Daily productivity [%] - Maquina 1")
    st.write(fig)
  with row1_col2:
    d_ini = pd.to_datetime(hoy).date()
    d_fin = pd.to_datetime(hoy).date()
    fig = line_graphic_main(df_orig,"maq2",d_ini,d_fin) 
    fig.update_layout(yaxis_title="Daily productivity [%] - Maquina 2")
    st.write(fig)
  with row1_col3:
    d_ini = pd.to_datetime(hoy).date()
    d_fin = pd.to_datetime(hoy).date()
    fig = line_graphic_main(df_orig,"maq3",d_ini,d_fin)
    fig.update_layout(yaxis_title="Daily productivity [%] - Maquina 3")
    st.write(fig)

  row3_col1, row3_col2, row3_col3 = st.columns(3)
  with row3_col1:
    d_ini = pd.to_datetime(hoy).date()
    d_fin = pd.to_datetime(hoy).date()
    fig = line_graphic_main(df_orig,"maq4",d_ini,d_fin)
    fig.update_layout(yaxis_title="Daily productivity [%] - Maquina 4")
    st.write(fig)
  with row3_col2:
    d_ini = pd.to_datetime(hoy).date()
    d_fin = pd.to_datetime(hoy).date()
    fig = line_graphic_main(df_orig,"maq5",d_ini,d_fin) 
    fig.update_layout(yaxis_title="Daily productivity [%] - Maquina 5")
    st.write(fig)
  with row3_col3:
    d_ini = pd.to_datetime(hoy).date()
    d_fin = pd.to_datetime(hoy).date()
    fig = line_graphic_main(df_orig,"maq6",d_ini,d_fin)
    fig.update_layout(yaxis_title="Daily productivity [%] - Maquina 6")
    st.write(fig)
    
with Maq1:
  Maquina = "maq1" 

  row0_spacer1, row0_col1, row0_spacer2, row0_col2, row0_spacer3 = st.columns((0.1, 6, 1, 2, 0.1))
  with row0_col1:
    d_ini = pd.to_datetime(hoy).date()
    d_fin = pd.to_datetime(hoy).date()
    fig = line_graphic_maq(df_orig,Maquina,d_ini,d_fin)
    fig.update_layout(xaxis_title="Date", yaxis_title="Productivity [%]",width=1100,height=350)
    st.write(fig)
    
    row1_spacer1, row1_col1, row1_col2 = st.columns((0.1, 3, 3))
    with row1_col1:
      d_ini = pd.to_datetime(inicio_semana_laboral).date()
      d_fin = pd.to_datetime(fin_semana_laboral).date()
      fig = line_graphic_maq(df_orig,Maquina,d_ini,d_fin) 
      st.write(fig)
    with row1_col2:
      d_ini = pd.to_datetime(inicio_mes).date()
      d_fin = pd.to_datetime(fin_mes).date()
      fig = line_graphic_maq(df_orig,Maquina,d_ini,d_fin)
      st.write(fig)
  with row0_col2:
    row0_col1.metric(label="### Productividad Diaria", value="100%", delta=80)
    row0_col2.metric(label="### Productividad Semanal", value="100%", delta=80)
    row0_col3.metric(label="### Productividad Mensual", value="100%", delta=80)

 #row1_col1, row1_col2, row1_col3 = st.columns(3)
time.sleep(1)   
    
