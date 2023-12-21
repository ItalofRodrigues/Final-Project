#Bibliotecas

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import folium
from haversine import haversine

#Funções

def clean_code(df1):
    """Está função tem como responsabilidade limpar o dataframe.
    Tipos de limpeza:
    1. Remoção dos dados NaN.
    2. Correção dos tipos das colunas de dados.
    3. Remoção dos espaços das variáveis de textos.
    4. Formatação da data.
    5. Limpeza da coluna de tempo. Remoção do texto da varável numérica.
    
    Input: Dataframe
    Output: Dataframe
    
    """

    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['City'] != 'NaN ' 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Type_of_vehicle'] != 'NaN ' 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Time_taken(min)'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Order_Date'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['ID'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()


    # Realizando a correção dos tipos.

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    df1['Delivery_person_Ratings'] =  df1['Delivery_person_Ratings'].astype( float )
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y' )
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # Retirando os espaços.

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # Comando para remover o texto de números

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split ('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1

def total_orders_by_day(df1):
    """Está função apresentará um gráfico de barras pertinente a quantidade
    de pedidos realizada por dia.
    """
    total_orders_by_day = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(total_orders_by_day, x='Order_Date', y='ID')
    return fig
    

def orders_by_traffic(df1):
    """Está função irá retornar um gráfico de pizza com as entregas por densidade de tráfego.
    """
    orders_by_traffic = (df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density'])
                                                                   .count()
                                                                   .reset_index())
    orders_by_traffic['entregas_perc'] = orders_by_traffic['ID'] / orders_by_traffic['ID'].sum()
    fig = px.pie(orders_by_traffic, values='entregas_perc', names='Road_traffic_density') 
    return fig

def volume_by_city_traffic(df1):
    """Está função irá retornar um gráfico dispersão pelas dimensões de cidade e tráfego.
    """
    volume_by_city_traffic = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density'])
                                                                                .count()
                                                                                .reset_index())
    fig = px.scatter(volume_by_city_traffic, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def orders_by_week(df1):
    """Está função retorna um gráfico de linhas pertinente a quantidade de entragas realizadas por semana.
    Na primeira linha, criamos a coluna 'Dias da semana', utilizamos a função strftime.
    """
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' ) #Está função cria a coluna referente ao dia da semana.
    orders_by_week = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    fig = px.line(orders_by_week, x='week_of_year', y='ID')
    return fig

def deliver_mean_by_week(df1):
    """Está função retorna um gráfico de linhas contenddo a quantidade de entrega média dos entregadores por semana.
    """
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig

def country_maps(df1):
    """Está função retorna um mapa com a localização central das cidades.
    """
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
        
    folium_static(map, width=1024, height=600)
#Leitura do arquivo

df = pd.read_csv('train.csv')

# Criando uma cópia do DataFrame.

df1 = clean_code(df)

#Visão Empresa - Barra Lateral

st.header('Marketplace - Visão da Empresa')

#Coluna Sidebar

image = Image.open('logo.webp') #Importação da Logo
st.sidebar.image(image, width=120)

st.sidebar.title(':red[Cury Company]')
st.sidebar.markdown('## Fast Delivery in Town')

st.sidebar.divider()

#Filtro
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor',
                 value=pd.datetime(2022, 4, 13), 
                 min_value=pd.datetime(2022, 2, 11), 
                 max_value=pd.datetime(2022, 4, 6), 
                 format='DD-MM-YYYY')

st.sidebar.divider()

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.divider()

st.sidebar.markdown('### Powered by Comunidade DS')

#Conectando o filtro
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#Layout no Streamlit

tab1, tab2, tab3 = st.tabs(['Visão de Planejamento', 'Visão Estratégica', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.header('Order by Day')
        fig = total_orders_by_day(df1)
        st.plotly_chart(fig, use_container_width=True)
       
        
    with st.container():
            
        col1, col2 = st.columns(2)
            
        with col1:
            st.header('Distribution of orders by traffic')
            fig = orders_by_traffic(df1)
            st.plotly_chart(fig, use_container_width=True) 

        with col2:
            st.header('Order by city and type of traffic.')
            fig = volume_by_city_traffic(df1)
            st.plotly_chart(fig, use_container_width=True) 

with tab2:
    with st.container():
        st.header('Order by Week')
        fig = orders_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)               
        
    with st.container():
        st.header('Order mean by deliveryman by week')
        fig = deliver_mean_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
                
    
with tab3:
    st.header('Central location by traffic')
    country_maps(df1)
           
