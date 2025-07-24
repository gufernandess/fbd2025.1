import pandas as pd
import panel as pn
import datetime
from sqlalchemy import text
from connection import create_db_connections

def create_exercicio_crud_view():
    try:
        pg_connection, engine = create_db_connections()
    except Exception as e:
        return pn.pane.Alert(f"Falha ao conectar ao banco de dados na aba de Exercício: {e}", alert_type='danger')


    EXERCICIOS_SUGESTOES = [
        'Caminhada', 'Corrida', 'Musculação', 'Yoga', 'Natação',
        'Funcional', 'Bicicleta', 'Futebol', 'Dança', 'Pilates'
    ]
    id_exercicio_input = pn.widgets.IntInput(name="ID do Exercício (para Consultar/Alterar/Excluir)", value=None, placeholder='Digite o ID...')
    id_usuario_input = pn.widgets.IntInput(name="ID do Usuário", placeholder='Digite o ID do usuário...')
    tipo_exercicio_input = pn.widgets.AutocompleteInput(name="Tipo de Exercício", options=EXERCICIOS_SUGESTOES, placeholder="Digite ou selecione um exercício...")
    duracao_minutos_input = pn.widgets.IntInput(name="Duração (minutos)", step=5, placeholder="Ex: 30")
    notas_exercicio_input = pn.widgets.TextAreaInput(name="Notas (opcional)", placeholder="Descreva detalhes do treino...", height=100)
    data_exercicio_input = pn.widgets.DatetimeInput(name="Data do Exercício", value=datetime.datetime.now())

    buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary')
    buttonInserir = pn.widgets.Button(name='Inserir', button_type='success')
    buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger')
    buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning')

    def queryAllExercicio():
        query = "SELECT * FROM exercicio ORDER BY data_exercicio DESC"
        df = pd.read_sql_query(query, engine)
        if 'data_exercicio' in df.columns:
            df['data_exercicio'] = pd.to_datetime(df['data_exercicio']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, layout='fit_data')

    def on_consultar_exercicio(event):
        try:
            id_alvo = id_exercicio_input.value
            if id_alvo is None:
                return queryAllExercicio()

            sql = text("SELECT * FROM exercicio WHERE id_exercicio = :id_param")
            df = pd.read_sql_query(sql, engine, params={"id_param": id_alvo})

            if df.empty:
                return pn.pane.Alert(f"Nenhum exercício encontrado com o ID: {id_alvo}", alert_type='warning')

            if not df.empty:
                row = df.iloc[0]
                id_usuario_input.value = int(row['id_usuario'])
                tipo_exercicio_input.value = row['tipo_exercicio']
                duracao_minutos_input.value = int(row['duracao_minutos'])
                notas_exercicio_input.value = row['notas_exercicio'] if pd.notna(row['notas_exercicio']) else ''
                data_exercicio_input.value = pd.to_datetime(row['data_exercicio'])

            return pn.widgets.Tabulator(df)
        except Exception as e:
            return pn.pane.Alert(f'Não foi possível consultar: {e}', alert_type='danger')

    def on_inserir_exercicio(event):
        cursor = None
        try:
            if not all([id_usuario_input.value, tipo_exercicio_input.value, duracao_minutos_input.value, data_exercicio_input.value]):
                if pn.state.notifications:
                    pn.state.notifications.error('Os campos ID do Usuário, Tipo, Duração e Data são obrigatórios!', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "INSERT INTO exercicio (tipo_exercicio, duracao_minutos, notas_exercicio, data_exercicio, id_usuario) VALUES (%s, %s, %s, %s, %s)"

            notas_texto = notas_exercicio_input.value
            notas = notas_texto if isinstance(notas_texto, str) and notas_texto.strip() else None

            dados = (tipo_exercicio_input.value, duracao_minutos_input.value, notas, data_exercicio_input.value, id_usuario_input.value)
            cursor.execute(sql, dados)
            pg_connection.commit()

            if pn.state.notifications:
                pn.state.notifications.success('Exercício registrado com sucesso!')
            return queryAllExercicio()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível inserir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_atualizar_exercicio(event):
        cursor = None
        try:
            id_alvo = id_exercicio_input.value
            if id_alvo is None:
                if pn.state.notifications:
                    pn.state.notifications.error('Digite o ID do exercício que deseja atualizar.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "UPDATE exercicio SET tipo_exercicio = %s, duracao_minutos = %s, notas_exercicio = %s, data_exercicio = %s, id_usuario = %s WHERE id_exercicio = %s"

            notas_texto = notas_exercicio_input.value
            notas = notas_texto if isinstance(notas_texto, str) and notas_texto.strip() else None

            dados = (tipo_exercicio_input.value, duracao_minutos_input.value, notas, data_exercicio_input.value, id_usuario_input.value, id_alvo)
            cursor.execute(sql, dados)
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhum exercício encontrado com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Exercício atualizado com sucesso!')
            return queryAllExercicio()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível atualizar: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_excluir_exercicio(event):
        cursor = None
        try:
            id_alvo = id_exercicio_input.value
            if id_alvo is None:
                if pn.state.notifications:
                    pn.state.notifications.error('Digite o ID do exercício que deseja excluir.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "DELETE FROM exercicio WHERE id_exercicio = %s"
            cursor.execute(sql, (id_alvo,))
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhum exercício encontrado com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Exercício excluído com sucesso!')
            return queryAllExercicio()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível excluir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    tabela_interativa_exercicio = pn.Column(queryAllExercicio())

    def atualizar_tabela_exercicio(event):
        tabela_interativa_exercicio.objects = [on_atualizar_exercicio(event)]

    def inserir_tabela_exercicio(event):
        tabela_interativa_exercicio.objects = [on_inserir_exercicio(event)]

    def excluir_tabela_exercicio(event):
        tabela_interativa_exercicio.objects = [on_excluir_exercicio(event)]

    def consultar_tabela_exercicio(event):
        tabela_interativa_exercicio.objects = [on_consultar_exercicio(event)]

    buttonConsultar.on_click(consultar_tabela_exercicio)
    buttonInserir.on_click(inserir_tabela_exercicio)
    buttonAtualizar.on_click(atualizar_tabela_exercicio)
    buttonExcluir.on_click(excluir_tabela_exercicio)

    controles_exercicio = pn.Column(
        '### 🏋️ Registro de Exercício CRUD',
        id_exercicio_input,
        id_usuario_input,
        tipo_exercicio_input,
        duracao_minutos_input,
        notas_exercicio_input,
        data_exercicio_input,
        pn.Row(buttonConsultar, buttonInserir),
        pn.Row(buttonAtualizar, buttonExcluir),
        sizing_mode="fixed", width=400
    )

    return pn.Row(
        controles_exercicio,
        tabela_interativa_exercicio
    )
