import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from utils import Header, make_dash_table
import dash_table
import pandas as pd
import pathlib
import dash_cytoscape as cyto
import plotly.express as px
import random as rd

from app import m_Table
#Generating Hexadecimal numbers
r = lambda: rd.randint(0,150)

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()


df_current_prices = pd.read_csv(DATA_PATH.joinpath("df_current_prices.csv"))
df_hist_prices = pd.read_csv(DATA_PATH.joinpath("df_hist_prices.csv"))
df_avg_returns = pd.read_csv(DATA_PATH.joinpath("df_avg_returns.csv"))
df_after_tax = pd.read_csv(DATA_PATH.joinpath("df_after_tax.csv"))
df_recent_returns = pd.read_csv(DATA_PATH.joinpath("df_recent_returns.csv"))
df_graph = pd.read_csv(DATA_PATH.joinpath("df_graph.csv"))


def create_layout(app):
    return html.Div(
        [
            Header(app),
            # page 2
            html.Div(
                [
                    # Tabelas Arquivos
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        ["Arquivo de Topologia"], className="subtitle padded"
                                    ),
                                    dcc.Upload(id='topology',
                                                children = html.Div([
                                                                    html.A('Arraste ou Selecione o Arquivo')
                                                                    ]),),
                                    # html.Div(id = 'topology_table')
                                    dash_table.DataTable(id='topology_table', editable=True,row_deletable=False,page_action='none',
                                    style_table={'height': '300px', 'overflowY': 'auto'}),
                                ],
                                className="six columns",
                            ),
                            # html.Button('Add Row', id='editing-rows-button', n_clicks=0),
                            html.Div(
                                [
                                    html.H6(
                                        ["Arquivo de Medidas"],
                                        className="subtitle padded",
                                    ),
                                    dcc.Upload(id='meansured',
                                                children = html.Div([
                                                                    html.A('Arraste ou Selecione o Arquivo')
                                                                    ]),),
                                    # html.Div(id = 'meansured_table'),
                                    dash_table.DataTable(id='meansured_table',columns=[{"name": i, "id": i} for i in m_Table.columns],
data=m_Table.to_dict('records'),editable=True,row_deletable= False,page_action='none',
                                    style_table={'height': '300px','overflowY': 'auto'},row_selectable="multi", selected_rows=list()),
                                    # html.Button('Add Row', id='editing-rows-button', n_clicks=0)
                                ],
                                className="six columns",
                            ),
                            
                        ],
                        className="row ",
                    ),
                    # Grafo da Topologia
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6("Grafo da Rede Recebida", className="subtitle padded"),
                                    html.Div(id='dd-output-container'),
                                    html.Div(id='intermediate-value', style={'display': 'none'}),
                                    cyto.Cytoscape(
                                        id='cytoscape',
                                        elements={},
                                        selectedEdgeData=[],
                                        selectedNodeData=[],
                                        #layout={'name': 'none'}, # 'cose','grid'
                                        style={'width': '700px', 'height': '500px'},
                                        stylesheet = [
                                            {
                                                'selector': 'node',
                                                'style': {
                                                    'label': 'data(id)',
                                                    'shape': 'polygon',
                                                    'shape-polygon-points': '-0.2, -1, 0.2, -1, 0.2, 1, -0.2, 1',
                                                    'background-color': 'black'
                                                }
                                            },
                                            {
                                                'selector': ':selected',
                                                'style': {
                                                    'background-color': 'SteelBlue',
                                                }
                                            },
                                            {
                                                'selector': 'edge',
                                                'style': {
                                                    # "curve-style": "taxi",
                                                    "taxi-turn": 20,
                                                    "taxi-turn-min-distance": 5
                                                }
        
                                            }
                                        ],
                                        responsive = True
                                    ),
                                ],
                                className="twelve columns",
                            ),

                            html.Div(
                                [                                
                                    html.Div([html.H6('Propriedades')], id='properites-title', className='subtitle padded'),
                                    
                                    dash_table.DataTable(id='chkMeasurements', editable=True, page_action='none',
                                                         style_table={"margin-left": "15px", 'overflowY': 'auto'}, row_selectable='multi'),

                                    # dcc.Checklist(
                                    #     id='chkMeasurements',
                                    #     options=[],
                                    #     value=[],
                                    #     labelStyle={'display': 'inline-block', 'margin-left': '15px'}
                                    # ),  
                                    # html.P(),
                                    html.Button('Save Changes', id='btn-savePropertiesChanges',
                                                n_clicks=0, style={"margin-left": "15px"}),
                                ],
                                className="twelve columns"
                            ),
                        ],
                        className="row ",
                    ),
                    ####################################Analise de Criticalidades###############################
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        ["Criticalidades"], className="subtitle padded",
                                    ),
                                    dash_table.DataTable(id = 'criticalities',page_action='none',sort_action='native',
                                    style_table={'height': '300px','overflowY': 'auto'}, style_data_conditional=[{'if': {'column_id': 'Cricality', 'filter_query': '{Cricality} =' f'CSets_{x}'},
                                     'backgroundColor': '#%02X%02X%02X' % (r(),r(),r()),'color': 'white'} for x in range(1,100)]),
                                ],
                                className="six columns",
                            ),
                        ],
                        className="row ",
                    ),
                    ########################################## Plot J(x)######################################
                    html.Div([
                    dcc.Graph(id="graph"),

                    ]),
                    # Resultado Estimacao
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        ["Estado Estimado"], className="subtitle padded"
                                    ),
                                    html.Div(id='input-se-top', style={'display': 'none'}),
                                    html.Div(id='input-se-med', style={'display': 'none'}),
                                    html.Div(id='output_state', style={'display': 'none'}),
                                    html.Div(id='output_med', style={'display': 'none'}),
                                    dash_table.DataTable(id = 'se_table',page_action='none',
                                    style_table={'height': '300px','overflowY': 'auto'}),
                                ],
                                className="six columns",
                            ),
                        ],
                        className="row ",
                    ),
                    # Resultado Medidas
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        ["Medidas Filtradas"], className="subtitle padded",
                                    ),
                                    dash_table.DataTable(id = 'se_meansured_table',page_action='none',
                                    style_table={'height': '300px','overflowY': 'auto'},style_data_conditional=[{
            'if': {
                'column_id': 'Error_Normalize',
                'filter_query': '{Error_Normalize} > 3'
            },
            'backgroundColor': 'indianred',
            'color': 'white'
        },]),
                                ],
                                className="six columns",
                            ),
                        ],
                        className="row ",
                    ),
                    # Row 5
                    # Next Element in the page
                
                ],
                className="sub_page",
            ),
        ],
        className="page",
    )
