import panel as pn

from user import create_usuario_crud_view
from sleep import create_sono_crud_view
from lunch import create_refeicao_crud_view
from goal import create_meta_crud_view
from exercise import create_exercicio_crud_view
from hydration import create_hidratacao_crud_view
from search import create_pesquisa_view

pn.extension(sizing_mode="stretch_width", notifications=True)
pn.extension('tabulator')

dashboard_tabs = pn.Tabs(
    ('👤 Usuário', create_usuario_crud_view()),
    ('🛌 Sono', create_sono_crud_view()),
    ('🍽️ Refeição', create_refeicao_crud_view()),
    ('🎯 Metas', create_meta_crud_view()),
    ('🏋️ Exercício', create_exercicio_crud_view()),
    ('💧 Hidratação', create_hidratacao_crud_view()),
    ('🔎 Pesquisa', create_pesquisa_view()),
    dynamic=True
)


template = pn.template.FastListTemplate(
    site="Health Tracker",
    main=[dashboard_tabs],
    header_background="#007BFF",
)

template.servable()
