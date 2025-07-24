import pandas as pd
import panel as pn
import datetime
from sqlalchemy import text
from connection import create_db_connections

def create_refeicao_crud_view():
    try:
        pg_connection, engine = create_db_connections()
    except Exception as e:
        return pn.pane.Alert(f"Falha ao conectar ao banco de dados na aba de Refeição: {e}", alert_type='danger')

    TIPOS_REFEICAO = ['Café da manhã', 'Almoço', 'Jantar', 'Lanche', 'Lanche da tarde']
    id_refeicao_input = pn.widgets.IntInput(name="ID da Refeição (para Consultar/Alterar/Excluir)", value=None, placeholder='Digite o ID...')
    id_usuario_input = pn.widgets.IntInput(name="ID do Usuário", placeholder='Digite o ID do usuário...')
    tipo_refeicao = pn.widgets.Select(name="Tipo de Refeição", options=TIPOS_REFEICAO)
    descricao_refeicao = pn.widgets.TextAreaInput(name="Descrição da Refeição", placeholder="Descreva o que você comeu...", height=120)
    foto_refeicao = pn.widgets.TextInput(name="URL da Foto (opcional)", placeholder="https://exemplo.com/foto.jpg")
    data_refeicao = pn.widgets.DatetimeInput(name="Data e Hora da Refeição", value=datetime.datetime.now())

    buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary')
    buttonInserir = pn.widgets.Button(name='Inserir', button_type='success')
    buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger')
    buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning')

    def queryAllRefeicao():
        query = "SELECT * FROM refeicao ORDER BY data_refeicao DESC"
        df = pd.read_sql_query(query, engine)
        if 'data_refeicao' in df.columns:
            df['data_refeicao'] = pd.to_datetime(df['data_refeicao']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, layout='fit_data')

    def on_consultar_refeicao(event):
        try:
            id_alvo = id_refeicao_input.value
            if id_alvo is None:
                return queryAllRefeicao()

            sql = text("SELECT * FROM refeicao WHERE id_refeicao = :id_param")
            df = pd.read_sql_query(sql, engine, params={"id_param": id_alvo})

            if df.empty:
                return pn.pane.Alert(f"Nenhuma refeição encontrada com o ID: {id_alvo}", alert_type='warning')

            if not df.empty:
                row = df.iloc[0]
                id_usuario_input.value = int(row['id_usuario'])
                tipo_refeicao.value = row['tipo_refeicao']
                descricao_refeicao.value = row['descricao_refeicao']
                foto_refeicao.value = row['foto_refeicao'] if pd.notna(row['foto_refeicao']) else ''
                data_refeicao.value = pd.to_datetime(row['data_refeicao'])

            return pn.widgets.Tabulator(df)
        except Exception as e:
            return pn.pane.Alert(f'Não foi possível consultar: {e}', alert_type='danger')

    def on_inserir_refeicao(event):
        cursor = None
        try:
            if not all([id_usuario_input.value, tipo_refeicao.value, descricao_refeicao.value, data_refeicao.value]):
                if pn.state.notifications:
                    pn.state.notifications.error('Preencha os campos obrigatórios!', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "INSERT INTO refeicao (tipo_refeicao, descricao_refeicao, foto_refeicao, data_refeicao, id_usuario) VALUES (%s, %s, %s, %s, %s)"

            foto_texto = foto_refeicao.value
            foto_url = foto_texto if isinstance(foto_texto, str) and foto_texto.strip() else None

            dados = (tipo_refeicao.value, descricao_refeicao.value, foto_url, data_refeicao.value, id_usuario_input.value)
            cursor.execute(sql, dados)
            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Refeição registrada com sucesso!')
            return queryAllRefeicao()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível inserir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_atualizar_refeicao(event):
        cursor = None
        try:
            id_alvo = id_refeicao_input.value
            if id_alvo is None:
                if pn.state.notifications:
                    pn.state.notifications.error('Digite o ID da refeição que deseja atualizar.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "UPDATE refeicao SET tipo_refeicao = %s, descricao_refeicao = %s, foto_refeicao = %s, data_refeicao = %s, id_usuario = %s WHERE id_refeicao = %s"

            foto_texto = foto_refeicao.value
            foto_url = foto_texto if isinstance(foto_texto, str) and foto_texto.strip() else None

            dados = (tipo_refeicao.value, descricao_refeicao.value, foto_url, data_refeicao.value, id_usuario_input.value, id_alvo)
            cursor.execute(sql, dados)
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhuma refeição encontrada com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Refeição atualizada com sucesso!')
            return queryAllRefeicao()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível atualizar: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_excluir_refeicao(event):
        cursor = None
        try:
            id_alvo = id_refeicao_input.value
            if id_alvo is None:
                if pn.state.notifications:
                    pn.state.notifications.error('Digite o ID da refeição que deseja excluir.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "DELETE FROM refeicao WHERE id_refeicao = %s"
            cursor.execute(sql, (id_alvo,))
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhuma refeição encontrada com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Refeição excluída com sucesso!')
            return queryAllRefeicao()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível excluir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    tabela_interativa_refeicao = pn.Column(queryAllRefeicao())

    def atualizar_tabela_refeicao(event):
        tabela_interativa_refeicao.objects = [on_atualizar_refeicao(event)]

    def inserir_tabela_refeicao(event):
        tabela_interativa_refeicao.objects = [on_inserir_refeicao(event)]

    def excluir_tabela_refeicao(event):
        tabela_interativa_refeicao.objects = [on_excluir_refeicao(event)]

    def consultar_tabela_refeicao(event):
        tabela_interativa_refeicao.objects = [on_consultar_refeicao(event)]

    buttonConsultar.on_click(consultar_tabela_refeicao)
    buttonInserir.on_click(inserir_tabela_refeicao)
    buttonAtualizar.on_click(atualizar_tabela_refeicao)
    buttonExcluir.on_click(excluir_tabela_refeicao)

    controles_refeicao = pn.Column(
        '### 🍽️ Registro de Refeição CRUD',
        id_refeicao_input,
        id_usuario_input,
        tipo_refeicao,
        descricao_refeicao,
        foto_refeicao,
        data_refeicao,
        pn.Row(buttonConsultar, buttonInserir),
        pn.Row(buttonAtualizar, buttonExcluir),
        sizing_mode="fixed", width=400
    )

    return pn.Row(
        controles_refeicao,
        tabela_interativa_refeicao
    )
