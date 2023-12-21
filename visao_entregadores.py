#Bibliotecas

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import folium
from haversine import haversine

#___________________________________________
#                   funções
#___________________________________________

def clean_code(df1):
    """Está função tem como responsabilidade limpar o dataframe.
    Tipos de limpeza:
    1. Remoção dos dados NaN.
    2. Correção dos tipos das colunas de dados.
    3. Remoção dos espaços das variáveis de textos.
    4. Formatação da data.
    5. Limpeza da coluna de tempo. Remoção do texto da varável  numérica.
    
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
    
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Delivery_person_Ratings'] != 'NaN '
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


def top_delivers(df1, top_asc):
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Delivery_person_ID', 'City']].groupby(['Delivery_person_ID', 'City'])
                                                                                      .min()
                                                                                      .sort_values(['City','Time_taken(min)'], ascending=top_asc)
                                                                                      .reset_index())

    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian',:].head(10)
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban',:].head(10)
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban',:].head(10)

    df2 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
    return df2


#Leitura do arquivo

df = pd.read_csv('train.csv')

#Cópia e limpeza:

df1 = clean_code(df)

#Título Visão dos Entregadores
st.title('Marketplace - Visão dos Entregadores')

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

#=============================================
# LAYOUT STREAMLIT
#=============================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        
        st.title(':red[Overall Metrics]')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            st.text('Older Age')
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('', maior_idade)
            
        with col2:
            st.text('Minor Age')
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('', menor_idade)
        
        with col3:
            st.text('Best Condition')
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('', melhor_condicao)
        
        with col4:
            st.text('Worst Condition')
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('', pior_condicao)
            
        with st.container():
            
            st.markdown("""___""")
            st.title(':red[Rating]')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.text('Rating per courier')
                df_avg_ratings_per_deliver =  (df1.loc[:, ['Delivery_person_Ratings','Delivery_person_ID']].groupby(['Delivery_person_ID'])
                                                                                                           .mean()
                                                                                                           .reset_index())
                st.dataframe(df_avg_ratings_per_deliver)

                
            with col2:
                st.text('Rating and standard deviation by traffic type')
                
                deviation_mean_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby(['Road_traffic_density'])
                                                                .agg( {'Delivery_person_Ratings': ['mean', 'std'] }).reset_index() )

                deviation_mean_by_traffic.columns = ['Road_traffic_density', 'delivery_mean', 'delivery_std']


                st.dataframe(deviation_mean_by_traffic)
                
                st.text('Rating and standard deviation by weather conditions')
                
                mean_deviation_by_weatherconditions = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby(['Weatherconditions'])
                .agg( {'Delivery_person_Ratings': ['mean', 'std'] } ).reset_index() )

                mean_deviation_by_weatherconditions.columns = ['Weatherconditions', 'Delivery_mean', 'Delivery_std']

                st.dataframe(mean_deviation_by_weatherconditions)
                
        with st.container():
            
            st.markdown("""___""")
            st.title(':red[Delivery Speed]')
            
            col1, col2 = st.columns(2)
            with col1:
                st.text('Top 10 fastest couriers by city')
                df2 = top_delivers(df1, top_asc=True)
                st.dataframe(df2)
                
                
                
            with col2:
                st.text('Top 10 slowest couriers by city')
                df2 = top_delivers(df1, top_asc=False)
                st.dataframe(df2)
            

