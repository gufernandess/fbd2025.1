import pandas as pd
import panel as pn
import datetime
import random
from sqlalchemy import text
from connection import create_db_connections

def create_usuario_crud_view():
    try:
        pg_connection, engine = create_db_connections()
    except Exception as e:
        return pn.pane.Alert(f"Falha ao conectar ao banco de dados na aba de Usuário: {e}", alert_type='danger')

    def simular_hash_bcrypt():
        alfabeto_bcrypt = './ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        prefixo = '$2b$12$'
        salt_simulado = ''.join(random.choices(alfabeto_bcrypt, k=22))
        hash_simulado = ''.join(random.choices(alfabeto_bcrypt, k=31))
        return f"{prefixo}{salt_simulado}{hash_simulado}"

    nome_usuario = pn.widgets.TextInput(name="Nome do Usuário", placeholder='Digite o nome')
    email = pn.widgets.TextInput(name="E-mail", placeholder='Digite o e-mail')

    buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary')
    buttonInserir = pn.widgets.Button(name='Inserir', button_type='success')
    buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger')
    buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning')

    def queryAll():
        query = "SELECT id_usuario, nome_usuario, email, data_criacao_conta FROM usuario ORDER BY nome_usuario"
        df = pd.read_sql_query(query, engine)
        if 'data_criacao_conta' in df.columns:
            df['data_criacao_conta'] = pd.to_datetime(df['data_criacao_conta']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, layout='fit_data')

    def on_consultar(event):
        try:
            email_alvo = email.value.strip()
            if not email_alvo:
                return queryAll()

            sql = text("SELECT id_usuario, nome_usuario, email, data_criacao_conta FROM usuario WHERE email = :email_param")
            df = pd.read_sql_query(sql, engine, params={"email_param": email_alvo})

            if df.empty:
                return pn.pane.Alert(f"Nenhum usuário encontrado com o e-mail: {email_alvo}", alert_type='warning')

            if not df.empty:
                nome_usuario.value = df.iloc[0]['nome_usuario']

            return pn.widgets.Tabulator(df)
        except Exception as e:
            return pn.pane.Alert(f'Não foi possível consultar: {e}', alert_type='danger')

    def on_inserir(event):
        cursor = None
        try:
            if not nome_usuario.value or not email.value:
                if pn.state.notifications:
                    pn.state.notifications.error('Nome e E-mail são obrigatórios!', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "INSERT INTO usuario(nome_usuario, email, senha_hash, data_criacao_conta) VALUES (%s, %s, %s, %s)"
            dados = (
                nome_usuario.value,
                email.value,
                simular_hash_bcrypt(),
                datetime.datetime.now()
            )
            cursor.execute(sql, dados)
            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Usuário inserido com sucesso!')
            return queryAll()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível inserir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_atualizar(event):
        cursor = None
        try:
            if not nome_usuario.value or not email.value:
                if pn.state.notifications:
                    pn.state.notifications.error('Nome e E-mail são obrigatórios para atualizar!', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "UPDATE usuario SET nome_usuario = %s, senha_hash = %s WHERE email = %s"
            dados = (
                nome_usuario.value,
                simular_hash_bcrypt(),
                email.value
            )
            cursor.execute(sql, dados)
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhum usuário encontrado com o e-mail: {email.value}', alert_type='warning')
            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Usuário atualizado com sucesso!')
            return queryAll()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível atualizar: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_excluir(event):
        cursor = None
        try:
            if not email.value:
                if pn.state.notifications:
                    pn.state.notifications.error('O campo E-mail é obrigatório para excluir!', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "DELETE FROM usuario WHERE email = %s"
            email_alvo = (email.value,)
            cursor.execute(sql, email_alvo)
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhum usuário encontrado com o email: {email.value}', alert_type='warning')
            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Usuário excluído com sucesso!')
            return queryAll()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível excluir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    tabela_interativa = pn.Column(queryAll())

    def atualizar_tabela(event):
        tabela_interativa.objects = [on_atualizar(event)]

    def inserir_tabela(event):
        tabela_interativa.objects = [on_inserir(event)]

    def excluir_tabela(event):
        tabela_interativa.objects = [on_excluir(event)]

    def consultar_tabela(event):
        tabela_interativa.objects = [on_consultar(event)]

    buttonConsultar.on_click(consultar_tabela)
    buttonInserir.on_click(inserir_tabela)
    buttonAtualizar.on_click(atualizar_tabela)
    buttonExcluir.on_click(excluir_tabela)

    controles = pn.Column(
        '### 👤 Usuário CRUD',
        nome_usuario,
        email,
        pn.Row(buttonConsultar, buttonInserir),
        pn.Row(buttonAtualizar, buttonExcluir),
        sizing_mode="fixed", width=400
    )

    return pn.Row(
        controles,
        tabela_interativa
    )
