import pandas as pd
import panel as pn
import datetime
from sqlalchemy import text
from connection import create_db_connections

def create_meta_crud_view():
    try:
        pg_connection, engine = create_db_connections()
    except Exception as e:
        return pn.pane.Alert(f"Falha ao conectar ao banco de dados na aba de Metas: {e}", alert_type='danger')

    id_meta_input = pn.widgets.IntInput(name="ID da Meta (para Consultar/Alterar/Excluir)", value=None, placeholder='Digite o ID...')
    id_usuario_input = pn.widgets.IntInput(name="ID do Usuário", placeholder='Digite o ID do usuário...')
    tipo_meta_input = pn.widgets.TextInput(name="Tipo da Meta", placeholder="Ex: Passos Diários, Hidratação")
    valor_meta_input = pn.widgets.FloatInput(name="Valor da Meta", placeholder="Ex: 10000, 3000")
    unidade_meta_input = pn.widgets.TextInput(name="Unidade da Meta", placeholder="Ex: passos, ml, km")
    data_meta_input = pn.widgets.DatePicker(name="Data da Meta")

    buttonConsultar = pn.widgets.Button(name='Consultar', button_type='primary')
    buttonInserir = pn.widgets.Button(name='Inserir', button_type='success')
    buttonExcluir = pn.widgets.Button(name='Excluir', button_type='danger')
    buttonAtualizar = pn.widgets.Button(name='Atualizar', button_type='warning')

    def queryAllMetas():
        query = "SELECT * FROM meta ORDER BY data_meta DESC"
        df = pd.read_sql_query(query, engine)
        if 'data_meta' in df.columns:
            df['data_meta'] = pd.to_datetime(df['data_meta']).dt.strftime('%Y-%m-%d')
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, layout='fit_data')

    def on_consultar_meta(event):
        try:
            id_alvo = id_meta_input.value
            if id_alvo is None:
                return queryAllMetas()

            sql = text("SELECT * FROM meta WHERE id_meta = :id_param")
            df = pd.read_sql_query(sql, engine, params={"id_param": id_alvo})

            if df.empty:
                return pn.pane.Alert(f"Nenhuma meta encontrada com o ID: {id_alvo}", alert_type='warning')

            if not df.empty:
                row = df.iloc[0]
                id_usuario_input.value = int(row['id_usuario'])
                tipo_meta_input.value = row['tipo_meta']
                valor_meta_input.value = float(row['valor_meta'])
                unidade_meta_input.value = row['unidade_meta']
                data_meta_input.value = pd.to_datetime(row['data_meta']).date()

            return pn.widgets.Tabulator(df)
        except Exception as e:
            return pn.pane.Alert(f'Não foi possível consultar: {e}', alert_type='danger')

    def on_inserir_meta(event):
        cursor = None
        try:
            id_usuario = id_usuario_input.value
            data_meta = data_meta_input.value

            if not all([id_usuario, data_meta, tipo_meta_input.value, valor_meta_input.value, unidade_meta_input.value]):
                if pn.state.notifications:
                    pn.state.notifications.error('Preencha todos os campos obrigatórios!', duration=4000)
                return

            assert isinstance(data_meta, datetime.date)
            cursor = pg_connection.cursor()
            check_sql = "SELECT COUNT(*) FROM meta WHERE id_usuario = %s AND data_meta = %s"
            cursor.execute(check_sql, (id_usuario, data_meta))
            result = cursor.fetchone()
            if result and result[0] > 0:
                if pn.state.notifications:
                    pn.state.notifications.error(f'Este usuário já possui uma meta para o dia {data_meta.strftime("%Y-%m-%d")}.', duration=5000)
                return

            sql = "INSERT INTO meta (tipo_meta, valor_meta, unidade_meta, data_meta, id_usuario) VALUES (%s, %s, %s, %s, %s)"
            dados = (tipo_meta_input.value, valor_meta_input.value, unidade_meta_input.value, data_meta, id_usuario)
            cursor.execute(sql, dados)
            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Meta registrada com sucesso!')
            return queryAllMetas()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível inserir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_atualizar_meta(event):
        cursor = None
        try:
            id_alvo = id_meta_input.value
            id_usuario = id_usuario_input.value
            data_meta = data_meta_input.value

            if not all([id_alvo, id_usuario, data_meta, tipo_meta_input.value, valor_meta_input.value]):
                if pn.state.notifications:
                    pn.state.notifications.error('Para atualizar, preencha o ID da Meta e todos os outros campos!', duration=4000)
                return

            assert isinstance(data_meta, datetime.date)
            cursor = pg_connection.cursor()
            check_sql = "SELECT COUNT(*) FROM meta WHERE id_usuario = %s AND data_meta = %s AND id_meta != %s"
            cursor.execute(check_sql, (id_usuario, data_meta, id_alvo))
            result = cursor.fetchone()
            if result and result[0] > 0:
                if pn.state.notifications:
                    pn.state.notifications.error(f'Este usuário já possui OUTRA meta para o dia {data_meta.strftime("%Y-%m-%d")}.', duration=5000)
                return

            sql = "UPDATE meta SET tipo_meta = %s, valor_meta = %s, unidade_meta = %s, data_meta = %s, id_usuario = %s WHERE id_meta = %s"
            dados = (tipo_meta_input.value, valor_meta_input.value, unidade_meta_input.value, data_meta, id_usuario, id_alvo)
            cursor.execute(sql, dados)
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhuma meta encontrada com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Meta atualizada com sucesso!')
            return queryAllMetas()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível atualizar: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    def on_excluir_meta(event):
        cursor = None
        try:
            id_alvo = id_meta_input.value
            if id_alvo is None:
                if pn.state.notifications:
                    pn.state.notifications.error('Digite o ID da meta que deseja excluir.', duration=4000)
                return

            cursor = pg_connection.cursor()
            sql = "DELETE FROM meta WHERE id_meta = %s"
            cursor.execute(sql, (id_alvo,))
            if cursor.rowcount == 0:
                pg_connection.rollback()
                return pn.pane.Alert(f'Nenhuma meta encontrada com o ID: {id_alvo}', alert_type='warning')

            pg_connection.commit()
            if pn.state.notifications:
                pn.state.notifications.success('Meta excluída com sucesso!')
            return queryAllMetas()
        except Exception as e:
            if pg_connection: pg_connection.rollback()
            return pn.pane.Alert(f'Não foi possível excluir: {e}', alert_type='danger')
        finally:
            if cursor: cursor.close()

    tabela_interativa_meta = pn.Column(queryAllMetas())

    def atualizar_tabela_meta(event):
        tabela_interativa_meta.objects = [on_atualizar_meta(event)]

    def inserir_tabela_meta(event):
        tabela_interativa_meta.objects = [on_inserir_meta(event)]

    def excluir_tabela_meta(event):
        tabela_interativa_meta.objects = [on_excluir_meta(event)]

    def consultar_tabela_meta(event):
        tabela_interativa_meta.objects = [on_consultar_meta(event)]

    buttonConsultar.on_click(consultar_tabela_meta)
    buttonInserir.on_click(inserir_tabela_meta)
    buttonAtualizar.on_click(atualizar_tabela_meta)
    buttonExcluir.on_click(excluir_tabela_meta)

    controles_meta = pn.Column(
        '### 🎯 Metas CRUD',
        id_meta_input,
        id_usuario_input,
        tipo_meta_input,
        valor_meta_input,
        unidade_meta_input,
        data_meta_input,
        pn.Row(buttonConsultar, buttonInserir),
        pn.Row(buttonAtualizar, buttonExcluir),
        sizing_mode="fixed", width=400
    )

    return pn.Row(
        controles_meta,
        tabela_interativa_meta
    )
