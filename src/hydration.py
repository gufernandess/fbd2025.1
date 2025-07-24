import pandas as pd
import panel as pn
import datetime
from sqlalchemy import text
from connection import create_db_connections

def create_hidratacao_crud_view():
    try:
        pg_connection, engine = create_db_connections()
    except Exception as e:
        return pn.pane.Alert(f"Falha ao conectar ao banco de dados na aba de Hidratação: {e}", alert_type='danger')


    id_hidratacao_input = pn.widgets.IntInput(name="ID da Hidratação (para Consultar/Alterar/Excluir)", value=None, placeholder='Digite o ID...')
    id_usuario_input = pn.widgets.IntInput(name="ID do Usuário", placeholder='Digite o ID do usuário...')
    quantidade_ml_input = pn.widgets.IntInput(name="Quantidade (ml)", step=50, placeholder="Ex: 250")
    data_hidratacao_input = pn.widgets.DatetimeInput(name="Data do Registro", value=datetime.datetime.now())

    buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary')
    buttonInserir = pn.widgets.Button(name='Inserir', button_type='success')
    buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger')
    buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning')

    def queryAllHidratacao():
        query = "SELECT * FROM hidratacao ORDER BY data_hidratacao DESC"
        df = pd.read_sql_query(query, engine)
        if 'data_hidratacao' in df.columns:
            df['data_hidratacao'] = pd.to_datetime(df['data_hidratacao']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, layout='fit_data')

    def on_consultar_hidratacao(event):
        try:
            id_alvo = id_hidratacao_input.value
            if id_alvo is None:
                return queryAllHidratacao()

            sql = text("SELECT * FROM hidratacao WHERE id_hidratacao = :id_param")
            df = pd.read_sql_query(sql, engine, params={"id_param": id_alvo})

            if df.empty:
                return pn.pane.Alert(f"Nenhum registro de hidratação encontrado com o ID: {id_alvo}", alert_type='warning')

            if not df.empty:
                row = df.iloc[0]
                id_usuario_input.value = int(row['id_usuario'])
                quantidade_ml_input.value = int(row['quantidade_ml'])
                data_hidratacao_input.value = pd.to_datetime(row['data_hidratacao'])

            return pn.widgets.Tabulator(df)
        except Exception as e:
            return pn.pane.Alert(f'Não foi possível consultar: {e}', alert_type='danger')

    def on_inserir_hidratacao(event):
        cursor = None
        try:
            if not all([id_usuario_input.value, quantidade_ml_input.value, data_hidratacao_input.value]):
                if pn.state.notifications:
                    pn.state.notifications.error('Todos os campos são obrigatórios!', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "INSERT INTO hidratacao (quantidade_ml, data_hidratacao, id_usuario) VALUES (%s, %s, %s)"
            dados = (quantidade_ml_input.value, data_hidratacao_input.value, id_usuario_input.value)
            cursor.execute(sql, dados)
            pg_connection.commit()

            if pn.state.notifications:
                pn.state.notifications.success('Registro de hidratação inserido com sucesso!')
            return queryAllHidratacao()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível inserir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_atualizar_hidratacao(event):
        cursor = None
        try:
            id_alvo = id_hidratacao_input.value
            if id_alvo is None:
                if pn.state.notifications:
                    pn.state.notifications.error('Digite o ID do registro que deseja atualizar.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "UPDATE hidratacao SET quantidade_ml = %s, data_hidratacao = %s, id_usuario = %s WHERE id_hidratacao = %s"
            dados = (quantidade_ml_input.value, data_hidratacao_input.value, id_usuario_input.value, id_alvo)
            cursor.execute(sql, dados)
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhum registro encontrado com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Registro atualizado com sucesso!')
            return queryAllHidratacao()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível atualizar: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_excluir_hidratacao(event):
        cursor = None
        try:
            id_alvo = id_hidratacao_input.value
            if id_alvo is None:
                if pn.state.notifications:
                    pn.state.notifications.error('Digite o ID do registro que deseja excluir.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "DELETE FROM hidratacao WHERE id_hidratacao = %s"
            cursor.execute(sql, (id_alvo,))
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhum registro encontrado com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Registro excluído com sucesso!')
            return queryAllHidratacao()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível excluir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    tabela_interativa_hidratacao = pn.Column(queryAllHidratacao())

    def atualizar_tabela_hidratacao(event):
        tabela_interativa_hidratacao.objects = [on_atualizar_hidratacao(event)]

    def inserir_tabela_hidratacao(event):
        tabela_interativa_hidratacao.objects = [on_inserir_hidratacao(event)]

    def excluir_tabela_hidratacao(event):
        tabela_interativa_hidratacao.objects = [on_excluir_hidratacao(event)]

    def consultar_tabela_hidratacao(event):
        tabela_interativa_hidratacao.objects = [on_consultar_hidratacao(event)]

    buttonConsultar.on_click(consultar_tabela_hidratacao)
    buttonInserir.on_click(inserir_tabela_hidratacao)
    buttonAtualizar.on_click(atualizar_tabela_hidratacao)
    buttonExcluir.on_click(excluir_tabela_hidratacao)

    controles_hidratacao = pn.Column(
        '### 💧 Registro de Hidratação CRUD',
        id_hidratacao_input,
        id_usuario_input,
        quantidade_ml_input,
        data_hidratacao_input,
        pn.Row(buttonConsultar, buttonInserir),
        pn.Row(buttonAtualizar, buttonExcluir),
        sizing_mode="fixed", width=400
    )

    return pn.Row(
        controles_hidratacao,
        tabela_interativa_hidratacao
    )
