import pandas as pd
import panel as pn
import datetime
from sqlalchemy import text
from connection import create_db_connections

def create_sono_crud_view():
    try:
        pg_connection, engine = create_db_connections()
    except Exception as e:
        return pn.pane.Alert(f"Falha ao conectar ao banco de dados na aba de Sono: {e}", alert_type='danger')

    id_sono_input = pn.widgets.IntInput(name="ID do Sono (para Consultar/Alterar/Excluir)", value=None, placeholder='Digite o ID...')
    id_usuario_input = pn.widgets.IntInput(name="ID do Usuário", placeholder='Digite o ID do usuário...')
    data_inicio_sono = pn.widgets.DatetimeInput(name="Início do Sono")
    data_fim_sono = pn.widgets.DatetimeInput(name="Fim do Sono")
    qualidade_sono = pn.widgets.IntSlider(name="Qualidade do Sono", start=1, end=5, step=1, value=3)

    buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary')
    buttonInserir = pn.widgets.Button(name='Inserir', button_type='success')
    buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger')
    buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning')

    def queryAllSono():
        query = "SELECT * FROM sono ORDER BY data_inicio_sono DESC"
        df = pd.read_sql_query(query, engine)
        for col in ['data_inicio_sono', 'data_fim_sono']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, layout='fit_data')

    def on_consultar_sono(event):
        try:
            id_alvo = id_sono_input.value
            if id_alvo is None:
                return queryAllSono()

            sql = text("SELECT * FROM sono WHERE id_sono = :id_param")
            df = pd.read_sql_query(sql, engine, params={"id_param": id_alvo})

            if df.empty:
                return pn.pane.Alert(f"Nenhum registro de sono encontrado com o ID: {id_alvo}", alert_type='warning')

            if not df.empty:
                row = df.iloc[0]
                id_usuario_input.value = int(row['id_usuario'])
                data_inicio_sono.value = pd.to_datetime(row['data_inicio_sono'])
                data_fim_sono.value = pd.to_datetime(row['data_fim_sono'])
                qualidade_sono.value = int(row['qualidade_sono'])

            return pn.widgets.Tabulator(df)
        except Exception as e:
            return pn.pane.Alert(f'Não foi possível consultar: {e}', alert_type='danger')

    def on_inserir_sono(event):
        cursor = None
        try:
            inicio = data_inicio_sono.value
            fim = data_fim_sono.value
            id_usuario = id_usuario_input.value

            if not all([inicio, fim, id_usuario]):
                if pn.state.notifications:
                    pn.state.notifications.error('Todos os campos são obrigatórios!', duration=4000)
                return

            assert isinstance(inicio, datetime.datetime)
            assert isinstance(fim, datetime.datetime)

            duracao = (fim - inicio).total_seconds() / 60
            if duracao < 0:
                if pn.state.notifications:
                    pn.state.notifications.error('A data final não pode ser anterior à data inicial.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "INSERT INTO sono (data_inicio_sono, data_fim_sono, duracao_minutos, qualidade_sono, id_usuario) VALUES (%s, %s, %s, %s, %s)"
            dados = (inicio, fim, int(duracao), qualidade_sono.value, id_usuario)
            cursor.execute(sql, dados)
            pg_connection.commit()

            if pn.state.notifications:
                pn.state.notifications.success('Registro de sono inserido com sucesso!')

            return queryAllSono()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível inserir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_atualizar_sono(event):
        cursor = None
        try:
            id_alvo = id_sono_input.value
            inicio = data_inicio_sono.value
            fim = data_fim_sono.value

            if not all([id_alvo, inicio, fim]):
                if pn.state.notifications:
                    pn.state.notifications.error('Preencha o ID do Sono e as datas para atualizar!', duration=4000)
                return

            assert isinstance(inicio, datetime.datetime)
            assert isinstance(fim, datetime.datetime)

            duracao = (fim - inicio).total_seconds() / 60
            if duracao < 0:
                if pn.state.notifications:
                    pn.state.notifications.error('A data final não pode ser anterior à data inicial.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "UPDATE sono SET data_inicio_sono = %s, data_fim_sono = %s, duracao_minutos = %s, qualidade_sono = %s, id_usuario = %s WHERE id_sono = %s"
            dados = (inicio, fim, int(duracao), qualidade_sono.value, id_usuario_input.value, id_alvo)
            cursor.execute(sql, dados)

            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhum registro encontrado com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Registro atualizado com sucesso!')
            return queryAllSono()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível atualizar: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_excluir_sono(event):
        cursor = None
        try:
            id_alvo = id_sono_input.value
            if id_alvo is None:
                if pn.state.notifications:
                    pn.state.notifications.error('Digite o ID do registro que deseja excluir.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "DELETE FROM sono WHERE id_sono = %s"
            cursor.execute(sql, (id_alvo,))
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhum registro encontrado com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Registro excluído com sucesso!')
            return queryAllSono()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível excluir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()
    tabela_interativa_sono = pn.Column(queryAllSono())

    def atualizar_tabela_sono(event):
        tabela_interativa_sono.objects = [on_atualizar_sono(event)]

    def inserir_tabela_sono(event):
        tabela_interativa_sono.objects = [on_inserir_sono(event)]

    def excluir_tabela_sono(event):
        tabela_interativa_sono.objects = [on_excluir_sono(event)]

    def consultar_tabela_sono(event):
        tabela_interativa_sono.objects = [on_consultar_sono(event)]

    buttonConsultar.on_click(consultar_tabela_sono)
    buttonInserir.on_click(inserir_tabela_sono)
    buttonAtualizar.on_click(atualizar_tabela_sono)
    buttonExcluir.on_click(excluir_tabela_sono)

    controles_sono = pn.Column(
        '### 🛌 Registro de Sono CRUD',
        id_sono_input,
        id_usuario_input,
        data_inicio_sono,
        data_fim_sono,
        qualidade_sono,
        pn.Row(buttonConsultar, buttonInserir),
        pn.Row(buttonAtualizar, buttonExcluir),
        sizing_mode="fixed", width=400
    )

    return pn.Row(
        controles_sono,
        tabela_interativa_sono
    )
