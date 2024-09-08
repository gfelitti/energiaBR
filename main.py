import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
# Função para carregar os dados
@st.cache_data
def load_data():
    df = pd.read_csv('Tecnocracia 84 - energia gerada historicamente pelos estados - Long_Format_Energy_Data.csv')
    
    # Limpar e ajustar os dados
    df['geracao'] = pd.to_numeric(df['geracao'].str.replace(',', ''), errors='coerce')
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['tipo_energia'] = df['tipo_energia'].replace({
        'Geração total\n Total Generation': 'Geração Total',
        'Hidro\n Hydro': 'Hidrelétrica',
        'Eólica \n Wind': 'Eólica',
        'Solar \n Solar': 'Solar',
        'Nuclear \n Nuclear': 'Nuclear',
        'Termo\n Thermal': 'Termelétrica',
        'Bagaço de cana \n Sugar Cane Bagasse': 'Bagaço de Cana',
        'Lenha\n Firewood': 'Lenha',
        'Lixívia\n Black Liquor': 'Lixívia',
        'Out. Fontes renováveis\n Other Renewable Sources': 'Outras Renováveis',
        'Carvão vapor\n Steam Coal': 'Carvão',
        'Gás natural\n Natural Gas': 'Gás Natural',
        'Gás de coqueria\n Coke Oven Gas': 'Gás de Coqueria',
        'Óleo combustível\n Fuel Oil': 'Óleo Combustível',
        'Óleo diesel\n Diesel Oil': 'Óleo Diesel',
        'Out. Fontes não renováveis\n Other Non-Renewable Sources': 'Outras Não Renováveis'
    })
    return df

# Carregar os dados
df = load_data()

# Filtrar as opções de estado, removendo 'NORTE' e 'NORDESTE'
estados_validos = df['Estado'].unique().tolist()

# Organizar os estados em ordem alfabética, com 'BRASIL' como primeiro
estados_validos.sort()
if 'BRASIL' in estados_validos:
    estados_validos.remove('BRASIL')
estados_validos.insert(0, 'BRASIL')


# Selecionar o estado
estado_selecionado = st.sidebar.selectbox(
    'Selecione o estado', 
    estados_validos
)

# Filtrar os dados para o estado selecionado
df_estado = df[df['Estado'] == estado_selecionado]
df_estado = df_estado[df_estado['tipo_energia'] != 'Geração Total']
df_estado=df_estado.drop_duplicates(subset=['Year', 'tipo_energia'])

# Agrupar por tipo de energia e calcular percentuais
df_pivot = df_estado.pivot(index='Year', columns='tipo_energia', values='geracao')
df_pivot = df_pivot.fillna(0).loc[:, (df_pivot != 0).any(axis=0)]
df_percentual = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100

# Convertendo o DataFrame de volta para formato long para usar no Altair
df_long = df_percentual.reset_index().melt(id_vars='Year', var_name='tipo_energia', value_name='percentual')

# Encontrar a categoria dominante em cada ano
dominante_por_ano = df_percentual.idxmax(axis=1).reset_index()
dominante_por_ano.columns = ['Year', 'Dominante']

# Criar o gráfico de área empilhado usando Altair
area_chart = alt.Chart(df_long).mark_area().encode(
    x='Year:O',
    y='percentual:Q',
        color=alt.Color('tipo_energia:N', legend=alt.Legend(orient='bottom')),  # Legenda no pé do gráfico
      tooltip=[alt.Tooltip('Year:O', title='Ano'),
             alt.Tooltip('tipo_energia:N', title='Tipo de Energia'),
             alt.Tooltip('percentual:Q', title='Percentual', format='.2f')]  # Formatando o percentual
).properties(
    width=1200,
    height=800,
    title=f'Geração de Energia por Tipo em {estado_selecionado} (%)'
)

# Anotar a categoria dominante no topo de cada ano
dom_chart = alt.Chart(dominante_por_ano).mark_text(
    align='center',
    baseline='bottom',
    dx=3
).encode(
    x='Year:O',
    y=alt.Y('max(percentual):Q', title='Percentual (%)'),  # Colocar a anotação no topo do gráfico
    text='Dominante:N'
)

# Combinar o gráfico de área com as anotações
final_chart = area_chart + dom_chart

# Renderizar o gráfico no app Streamlit
st.altair_chart(final_chart)