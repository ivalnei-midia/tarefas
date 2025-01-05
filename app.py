import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# Configuração do layout para visualização em celular
st.set_page_config(page_title="Gerenciamento de Tarefas", layout="wide")

# Acessando as credenciais do arquivo secrets.toml
db_user = st.secrets["database"]["user"]
db_password = st.secrets["database"]["password"]
db_host = st.secrets["database"]["host"]
db_port = st.secrets["database"]["port"]
db_name = st.secrets["database"]["database"]

# Conexão com o banco de dados PostgreSQL
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)
c = conn.cursor()

# Função para adicionar tarefa
def add_tarefa(nome, tipo, prioridade, status):
    c.execute('INSERT INTO tarefas (nome, tipo, prioridade, status) VALUES (%s, %s, %s, %s)', 
              (nome, tipo, prioridade, status))
    conn.commit()

# Função para obter tarefas
def get_tarefas():
    c.execute('SELECT nome, tipo, prioridade, status FROM tarefas')
    return c.fetchall()

# Função para excluir tarefa
def delete_tarefa(id):
    c.execute('DELETE FROM tarefas WHERE id = %s', (id,))
    conn.commit()

# Função para atualizar tarefa
def update_tarefa(id, nome, tipo, prioridade, status):
    c.execute('UPDATE tarefas SET nome = %s, tipo = %s, prioridade = %s, status = %s WHERE id = %s', 
              (nome, tipo, prioridade, status, id))
    conn.commit()

# Interface do Streamlit
st.title('Gerenciamento de Tarefas')

# Seleção de página
page = st.sidebar.selectbox('Navegar', ['Adicionar Tarefa', 'Consultar Tarefas', 'Atualizar/Excluir Tarefa'])

if page == 'Adicionar Tarefa':
    st.subheader('Adicionar Nova Tarefa')
    with st.form(key='add_task'):
        nome = st.text_input('Nome da Tarefa')
        tipo = st.selectbox('Tipo', ['objeto', 'atividade'])
        prioridade = st.selectbox('Prioridade', [0, 1, 2])
        status = st.selectbox('Status', ['a fazer', 'fazendo', 'feito'])
        submit_button = st.form_submit_button(label='Adicionar Tarefa')
        if submit_button:
            add_tarefa(nome, tipo, prioridade, status)
            st.success('Tarefa adicionada com sucesso!')

elif page == 'Consultar Tarefas':
    st.subheader('Tarefas Cadastradas')
    search_query = st.text_input('Pesquisar por nome da tarefa')
    tarefas = get_tarefas()
    df = pd.DataFrame(tarefas, columns=['Nome', 'Tipo', 'Prioridade', 'Status'])

    # Filtrar tarefas com base na pesquisa
    if search_query:
        df = df[df['Nome'].str.contains(search_query, case=False)]

    st.dataframe(df)

elif page == 'Atualizar/Excluir Tarefa':
    st.subheader('Atualizar ou Excluir Tarefa')
    tarefas = get_tarefas()
    df = pd.DataFrame(tarefas, columns=['Nome', 'Tipo', 'Prioridade', 'Status'])

    if len(df) > 0:
        activity_id = st.number_input('ID da Tarefa para Atualizar ou Excluir', min_value=1, max_value=len(df), step=1)
    else:
        st.warning('Nenhuma tarefa cadastrada.')
        activity_id = None  # Ou defina um valor padrão

    if activity_id is not None and st.button('Excluir Tarefa'):
        delete_tarefa(activity_id)
        st.success('Tarefa excluída com sucesso!')

    with st.form(key='update_task'):
        if st.form_submit_button('Carregar Tarefa'):
            tarefa = df.iloc[activity_id - 1]  # Ajuste para acessar a linha correta
            nome_atual = tarefa['Nome']
            tipo_atual = tarefa['Tipo']
            prioridade_atual = tarefa['Prioridade']
            status_atual = tarefa['Status']

            nome = st.text_input('Nome da Tarefa', value=nome_atual)
            tipo = st.selectbox('Tipo', ['objeto', 'atividade'], index=['objeto', 'atividade'].index(tipo_atual))
            prioridade = st.selectbox('Prioridade', [0, 1, 2], index=[0, 1, 2].index(prioridade_atual))
            status = st.selectbox('Status', ['a fazer', 'fazendo', 'feito'], index=['a fazer', 'fazendo', 'feito'].index(status_atual))
            update_button = st.form_submit_button(label='Atualizar Tarefa')
            if update_button:
                update_tarefa(activity_id, nome, tipo, prioridade, status)
                st.success('Tarefa atualizada com sucesso!')
