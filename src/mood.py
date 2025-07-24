import pandas as pd
import panel as pn
import datetime
from sqlalchemy import text
from connection import create_db_connections

try:
    pg_connection, engine = create_db_connections()
except Exception as e:
    pn.pane.Alert(f"Falha ao conectar ao banco de dados: {e}", alert_type='danger').servable()
    exit()

pn.extension(sizing_mode="stretch_width", notifications=True)
pn.extension('tabulator')

ESTADOS_HUMOR_SUGESTOES = [
    'Feliz', 'Cansado', 'Ansioso(a)', 'Normal', 'Animado(a)',
    'Estressado(a)', 'Relaxado(a)', 'Motivado(a)', 'Sonolento(a)'
]

id_humor_input = pn.widgets.IntInput(name="ID do Humor (para Consultar/Alterar/Excluir)", value=None, placeholder='Digite o ID...')
id_usuario_input = pn.widgets.IntInput(name="ID do Usuário", placeholder='Digite o ID do usuário...')
estado_humor_input = pn.widgets.AutocompleteInput(name="Estado de Humor", options=ESTADOS_HUMOR_SUGESTOES, placeholder="Digite ou selecione um humor...")
nota_contexto_input = pn.widgets.TextAreaInput(name="Nota de Contexto (opcional)", placeholder="Descreva o motivo ou contexto...", height=100)
data_registro_input = pn.widgets.DatetimeInput(name="Data do Registro", value=datetime.datetime.now())

buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary')
buttonInserir = pn.widgets.Button(name='Inserir', button_type='success')
buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger')
buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning')

def queryAllHumor():
    query = "SELECT * FROM humor ORDER BY data_registro DESC"
    df = pd.read_sql_query(query, engine)
    if 'data_registro' in df.columns:
        df['data_registro'] = pd.to_datetime(df['data_registro']).dt.strftime('%Y-%m-%d %H:%M:%S')
    return pn.widgets.Tabulator(df, pagination='remote', page_size=10, layout='fit_data')

def on_consultar_humor(event):
    try:
        id_alvo = id_humor_input.value
        if id_alvo is None:
            return queryAllHumor()

        sql = text("SELECT * FROM humor WHERE id_humor = :id_param")
        df = pd.read_sql_query(sql, engine, params={"id_param": id_alvo})

        if df.empty:
            return pn.pane.Alert(f"Nenhum registro de humor encontrado com o ID: {id_alvo}", alert_type='warning')

        if not df.empty:
            row = df.iloc[0]
            id_usuario_input.value = int(row['id_usuario'])
            estado_humor_input.value = row['estado_humor']
            nota_contexto_input.value = row['nota_contexto'] if pd.notna(row['nota_contexto']) else ''
            data_registro_input.value = pd.to_datetime(row['data_registro'])

        return pn.widgets.Tabulator(df)
    except Exception as e:
        return pn.pane.Alert(f'Não foi possível consultar: {e}', alert_type='danger')

def on_inserir_humor(event):
    cursor = None
    try:
        if not all([id_usuario_input.value, estado_humor_input.value, data_registro_input.value]):
            if pn.state.notifications:
                pn.state.notifications.error('Os campos ID do Usuário, Estado de Humor e Data são obrigatórios!', duration=4000)
            return

        cursor = pg_connection.cursor()
        sql = """
            INSERT INTO humor (estado_humor, nota_contexto, data_registro, id_usuario)
            VALUES (%s, %s, %s, %s)
        """

        nota_texto = nota_contexto_input.value
        nota = None

        if isinstance(nota_texto, str):
            if nota_texto.strip():
                nota = nota_texto

        dados = (
            estado_humor_input.value,
            nota,
            data_registro_input.value,
            id_usuario_input.value
        )
        cursor.execute(sql, dados)
        pg_connection.commit()
        return queryAllHumor()
    except Exception as e:
        if pg_connection: pg_connection.rollback()
        return pn.pane.Alert(f'Não foi possível inserir: {e}', alert_type='danger')
    finally:
        if cursor: cursor.close()

def on_atualizar_humor(event):
    cursor = None
    try:
        id_alvo = id_humor_input.value
        if id_alvo is None:
            if pn.state.notifications:
                pn.state.notifications.error('Digite o ID do registro que deseja atualizar.', duration=4000)
            return

        cursor = pg_connection.cursor()
        sql = """
            UPDATE humor
            SET estado_humor = %s, nota_contexto = %s, data_registro = %s, id_usuario = %s
            WHERE id_humor = %s
        """

        nota_texto = nota_contexto_input.value
        nota = None

        if isinstance(nota_texto, str):
            if nota_texto.strip():
                nota = nota_texto

        dados = (
            estado_humor_input.value,
            nota,
            data_registro_input.value,
            id_usuario_input.value,
            id_alvo
        )
        cursor.execute(sql, dados)
        if cursor.rowcount == 0:
            pg_connection.rollback()
            return pn.pane.Alert(f'Nenhum registro encontrado com o ID: {id_alvo}', alert_type='warning')

        pg_connection.commit()
        return queryAllHumor()
    except Exception as e:
        if pg_connection: pg_connection.rollback()
        return pn.pane.Alert(f'Não foi possível atualizar: {e}', alert_type='danger')
    finally:
        if cursor: cursor.close()

def on_excluir_humor(event):
    cursor = None
    try:
        id_alvo = id_humor_input.value
        if id_alvo is None:
            if pn.state.notifications:
                pn.state.notifications.error('Digite o ID do registro que deseja excluir.', duration=4000)
            return

        cursor = pg_connection.cursor()
        sql = "DELETE FROM humor WHERE id_humor = %s"
        cursor.execute(sql, (id_alvo,))
        if cursor.rowcount == 0:
            pg_connection.rollback()
            return pn.pane.Alert(f'Nenhum registro encontrado com o ID: {id_alvo}', alert_type='warning')

        pg_connection.commit()
        return queryAllHumor()
    except Exception as e:
        if pg_connection: pg_connection.rollback()
        return pn.pane.Alert(f'Não foi possível excluir: {e}', alert_type='danger')
    finally:
        if cursor: cursor.close()

tabela_interativa_humor = pn.Column(queryAllHumor())

def atualizar_tabela_humor(event):
    tabela_interativa_humor.objects = [on_atualizar_humor(event)]

def inserir_tabela_humor(event):
    tabela_interativa_humor.objects = [on_inserir_humor(event)]

def excluir_tabela_humor(event):
    tabela_interativa_humor.objects = [on_excluir_humor(event)]

def consultar_tabela_humor(event):
    tabela_interativa_humor.objects = [on_consultar_humor(event)]

buttonConsultar.on_click(consultar_tabela_humor)
buttonInserir.on_click(inserir_tabela_humor)
buttonAtualizar.on_click(atualizar_tabela_humor)
buttonExcluir.on_click(excluir_tabela_humor)

controles_humor = pn.Column(
    '### 😊 Registro de Humor CRUD',
    id_humor_input,
    id_usuario_input,
    estado_humor_input,
    nota_contexto_input,
    data_registro_input,
    pn.Row(buttonConsultar, buttonInserir),
    pn.Row(buttonAtualizar, buttonExcluir),
    sizing_mode="fixed", width=400
)

app_humor = pn.Row(
    controles_humor,
    tabela_interativa_humor
).servable()
