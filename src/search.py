import pandas as pd
import panel as pn
import datetime
from typing import List, Any
from sqlalchemy import text
from connection import create_db_connections

def create_pesquisa_view():
    try:
        pg_connection, engine = create_db_connections()
    except Exception as e:
        return pn.pane.Alert(f"Falha ao conectar ao banco de dados na aba de Pesquisa: {e}", alert_type='danger')

    user_id_input = pn.widgets.IntInput(name="ID do Usuário", placeholder="Digite o ID...")
    search_user_button = pn.widgets.Button(name="Buscar Todos os Registros do Usuário", button_type='primary')

    top_users_button = pn.widgets.Button(name="Usuários Mais Ativos (Top 5)", button_type='default')
    sleep_quality_button = pn.widgets.Button(name="Melhor Média de Qualidade de Sono", button_type='default')

    diary_user_id_input = pn.widgets.IntInput(name="ID do Usuário", placeholder="Digite o ID...")
    diary_date_input = pn.widgets.DatePicker(name="Selecione o Dia")
    diary_search_button = pn.widgets.Button(name="Ver Diário do Dia", button_type='primary')

    results_area = pn.Column(pn.pane.Markdown("### Resultados da sua pesquisa aparecerão aqui."))

    def search_by_user(event):
        user_id = user_id_input.value
        if user_id is None:
            if pn.state.notifications:
                pn.state.notifications.warning('Por favor, digite um ID de usuário.', duration=3000)
            return

        results_area.loading = True

        resultados: List[Any] = [pn.pane.Markdown(f"## Registros para o Usuário ID: {user_id}")]

        tabelas = ['sono', 'refeicao', 'meta', 'exercicio', 'hidratacao', 'humor']

        for tabela in tabelas:
            try:
                sql = text(f"SELECT * FROM {tabela} WHERE id_usuario = :user_id ORDER BY 1 DESC")
                df = pd.read_sql_query(sql, engine, params={"user_id": user_id})

                if not df.empty:
                    resultados.append(pn.pane.Markdown(f"### Tabela: `{tabela}`"))
                    resultados.append(pn.widgets.Tabulator(df, layout='fit_data', page_size=5))
            except Exception:
                pass

        results_area.objects = resultados
        results_area.loading = False

    def get_top_users(event):
        results_area.loading = True
        sql = text("""
            SELECT u.nome_usuario, COALESCE(counts.total_registros, 0) as total_registros
            FROM usuario u
            LEFT JOIN (
                SELECT id_usuario, COUNT(*) as total_registros FROM (
                    SELECT id_usuario FROM sono UNION ALL
                    SELECT id_usuario FROM refeicao UNION ALL
                    SELECT id_usuario FROM meta UNION ALL
                    SELECT id_usuario FROM exercicio UNION ALL
                    SELECT id_usuario FROM hidratacao UNION ALL
                    SELECT id_usuario FROM humor
                ) as all_records
                GROUP BY id_usuario
            ) as counts ON u.id_usuario = counts.id_usuario
            ORDER BY total_registros DESC
            LIMIT 5;
        """)
        df = pd.read_sql_query(sql, engine)
        results_area.objects = [
            pn.pane.Markdown("### Top 5 Usuários Mais Ativos"),
            pn.widgets.Tabulator(df, layout='fit_data')
        ]
        results_area.loading = False

    def get_sleep_quality_avg(event):
        results_area.loading = True
        sql = text("""
            SELECT u.nome_usuario, ROUND(AVG(s.qualidade_sono), 2) as media_qualidade_sono
            FROM usuario u
            JOIN sono s ON u.id_usuario = s.id_usuario
            GROUP BY u.nome_usuario
            HAVING COUNT(s.id_sono) > 3 -- Apenas usuários com um número razoável de registros
            ORDER BY media_qualidade_sono DESC
            LIMIT 5;
        """)
        df = pd.read_sql_query(sql, engine)
        results_area.objects = [
            pn.pane.Markdown("### Usuários com Melhor Média de Qualidade de Sono (mín. 4 noites)"),
            pn.widgets.Tabulator(df, layout='fit_data')
        ]
        results_area.loading = False

    def search_diary(event):
        user_id = diary_user_id_input.value
        selected_date = diary_date_input.value

        if not all([user_id, selected_date]):
            if pn.state.notifications:
                pn.state.notifications.warning('Por favor, preencha o ID do usuário e a data.', duration=3000)
            return

        assert isinstance(selected_date, datetime.date)

        results_area.loading = True

        resultados: List[Any] = [pn.pane.Markdown(f"## Diário do Usuário {user_id} para {selected_date.strftime('%d/%m/%Y')}")]

        tabelas_datas = {
            'sono': 'data_inicio_sono', 'refeicao': 'data_refeicao', 'meta': 'data_meta',
            'exercicio': 'data_exercicio', 'hidratacao': 'data_hidratacao', 'humor': 'data_registro'
        }

        for tabela, coluna_data in tabelas_datas.items():
            try:
                sql = text(f"SELECT * FROM {tabela} WHERE id_usuario = :user_id AND {coluna_data}::date = :selected_date")
                df = pd.read_sql_query(sql, engine, params={"user_id": user_id, "selected_date": selected_date})
                if not df.empty:
                    resultados.append(pn.pane.Markdown(f"### {tabela.capitalize()}"))
                    resultados.append(pn.widgets.Tabulator(df, layout='fit_data'))
            except Exception:
                pass

        results_area.objects = resultados
        results_area.loading = False

    search_user_button.on_click(search_by_user)
    top_users_button.on_click(get_top_users)
    sleep_quality_button.on_click(get_sleep_quality_avg)
    diary_search_button.on_click(search_diary)

    accordion = pn.Accordion(
        ('🔎 Pesquisar Todos os Registros por Usuário', pn.Column(user_id_input, search_user_button)),
        ('🏆 Relatórios e Rankings', pn.Column(top_users_button, sleep_quality_button)),
        ('🗓️ Diário do Usuário por Dia', pn.Column(diary_user_id_input, diary_date_input, diary_search_button)),
        sizing_mode="fixed", width=400
    )

    return pn.Row(
        accordion,
        results_area
    )
