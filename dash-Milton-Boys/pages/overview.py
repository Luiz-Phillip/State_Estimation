import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import Header, make_dash_table

import pandas as pd
import pathlib

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()


df_fund_facts = pd.read_csv(DATA_PATH.joinpath("df_fund_facts.csv"))
df_price_perf = pd.read_csv(DATA_PATH.joinpath("df_price_perf.csv"))


def create_layout(app):
    # Page layouts
    return html.Div(
        [
            html.Div([Header(app)]),
            # page 1
            html.Div(
                [
                    # Row 3
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                    [html.Img(
                                        src=app.get_asset_url("logonew.png"),
                                        className="logo",
                                        style={'height':'60%', 'width':'60%'},
                                    ),],
                                    style={
                                        "display": "inline-block",
                                        "width": "20%"
                                        },
                                    ),
                                    #html.H5("Estimação de Estado"),
                                    html.Div([
                                    #html.Br([]),
                                    html.P(
                                        "\
                                        A Estimação de Estado (EE) se encarrega do processamento de medidas (observações) referentes ao comportamento (estado)\
                                        de um sistema de potência que opera no regime de equilíbrio entre carga e geração. \
                                            O estado para este regime de operação caracteriza-se pelas tensões de barra (em magnitude e ângulo de  \
                                        ",
                                        
                                        style={"color": "#ffffff"},
                                        className="row",
                                    ),
                                    ],
                                    style={
                                            "display": "inline-block",
                                            "width": "77%",
                                            "margin-left": "5px",
                                            "verticalAlign": "top",
                                            "font-size":"150%",
                                            }
                                    ),
                                    html.P(
                                        "\
                                            fase). Conhecer o estado operativo de um sistema constitui tarefa de vital importância para que se possa decidir \
                                                sobre como conduzir ações que visem aspectos relativos à continuidade de serviço e segurança.\
                                                    ",
                                        
                                        style={"color": "#ffffff",
                                                "width": "98%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                                        className="row",
                                    ),
                                    html.P(
                                        "\
                                            O usuário da presente ferramenta de aprendizado (ESE) encontrará duas formas de fornecer dados de entrada para a EE: \
                                            aqueles obtidos por meio da simulação de condições operativas em um Fluxo de Potência (FP) \
                                                — que servirá para a geração de medidas a serem processadas \
                                                    — ou através de um arquivo de dados de um sistema de medição criado para este fim. \
                                                        Os dados de entrada poderão ser editados conforme instruções fornecidas na pasta de Ajuda da ESE.\
                                                    ",
                                        
                                        style={"color": "#ffffff",
                                                "width": "95%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                                        className="row",
                                    ),
                                    html.P(
                                        "\
                                        Após alguns testes iniciais com a ESE, o usuário poderá avançar em suas simulações criando situações diversas, por exemplo, aquelas relativas a:\
                                             presença de medidas portadoras de erros grosseiros, indisponibilidades de medição e alterações na configuração da rede.\
                                                A ESE está estruturada em módulos, a saber:\
                                                    ",
                                        
                                        style={"color": "#ffffff",
                                                "width": "95%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                                        className="row",
                                    ),
                                ],
                                className="product",
                            )
                        ],
                        className="row",
                    ),

                    # Row 3
                    html.Div(
                        
                         
                        [
                            "A ESE está estruturada em módulos, a saber:"
                            
                        ],
                        className="product",
                        style={"color": "#ffffff",
                                        "width": "100%",
                                        "verticalAlign": "top",
                                        "font-size":"150%"
                                },
                        
                        #className="row",
                    ),
                    html.Div(
                        [
                            html.P(
                                [
                                    "Dados de Entrada para o FP\
                                    "
                                    
                                ],
                            ),
                            html.P( [" • rede — configuração desejada da rede e valores de seus parâmetros elétricos;",],),
                            html.P( [" • barras — geração, perfil de carga e elemento em derivação (??). Os dados de barras não são necessários, quando estiverem disponíveis valores telemedidos.",],),
                        ],
                        className="product",
                                style={"color": "#ffffff",
                                                "width": "100%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                        #className="row",
                    ),
                    html.Div(
                        [
                            html.P(
                                [
                                    "Dados de Saída do FP — Sistema de Medição\
                                    "
                                    
                                ],
                            ),
                            html.P( [" Com resultado do FP, o usuário deverá selecionar o sistema de medição para a EE, \
                                informando em uma tabela própria para tal: tipo de medidor (fluxo/injeção de potência ativa/reativa, magnitude/ângulo de tensão, parte real/imaginária de correntes), \
                                localização (barra/ramo da rede elétrica), valor da medida e respectivo desvio-padrão. \
                                Também, há um campo destinado a especificar o limiar de detecção de erros grosseiros de medição. Caso não utilize o FP para gerar medidas, crie um arquivo com dados de telemedidas.",],),
                            
                        ],
                        className="product",
                                style={"color": "#ffffff",
                                                "width": "100%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                        #className="row",
                    ),
                    html.Div(
                        [
                            html.P(
                                [
                                    "Análise Observabilidade/Criticalidade\
                                    "
                                    
                                ],
                            ),
                            html.P( ["A ESE avalia a condição de observabilidade da rede, considerando também possíveis indisponibilidades de medição (futuramente, também de ramos da rede)\
                                 o que constitui a análise de criticalidades. O usuário poderá definir até que cardinalidade de medidas formando grupos (tomadas duas-a-duas, três-a-três, etc.)\
                                      deseja realizar tal análise.",],),
                            
                        ],
                        className="product",
                                style={"color": "#ffffff",
                                                "width": "100%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                        #className="row",
                    ),
                    html.Div(
                        [
                            html.P(
                                [
                                    "Estimação de Estado\
                                    "
                                    
                                ],
                            ),
                            html.P( ["A ESE obtém o estado estimado, e com ele as medidas estimadas correspondentes àquelas que foram recebidas inicialmente para processamento (telemedidas ou valores obtidos por simulação). Em seguida, a ESE calcula os resíduos (normalizados) da estimação e, quando for o caso, assinala as medidas que ultrapassarem o limiar pré-estabelecido para a detecção de erros grosseiros.",],),
                            
                        ],
                        className="product",
                                style={"color": "#ffffff",
                                                "width": "100%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                        #className="row",
                    ),
                    html.Div(
                        [
                            html.P(
                                [
                                    "Estimador com Capacidade de Previsão (FASE)\
                                    "
                                    
                                ],
                            ),
                            html.P( ["Este módulo (em construção) irá fornecer valores previstos para o estado/medidas a serem usados para a construção de uma etapa de validação a priori (análise de inovações) dos valores de medidas recebidas para processamento.",],),
                            
                        ],
                        className="product",
                                style={"color": "#ffffff",
                                                "width": "100%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                        #className="row",
                    ),
                    html.Div(
                        [
                            
                            html.P(
                                [
                                    "Estimador com Capacidade de Previsão (FASE)\
                                    "
                                    
                                ],
                            ),
                            html.P( ["Este módulo (em construção) irá fornecer valores previstos para o estado/medidas a serem usados para a construção de uma etapa de validação a priori (análise de inovações) dos valores de medidas recebidas para processamento.",],),
                            
                        ],
                        className="product",
                                style={"color": "#ffffff",
                                                "width": "100%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                        #className="row",
                    ),
                    html.Div(
                        [
                            
                            html.P(
                                [
                                    "Estimador para Redes de Distribuição\
                                    "
                                    
                                ],
                            ),
                            html.P( ["Este módulo (em construção) tratará o problema da estimação de estado em sistemas de distribuição com tratamento trifásico e diante da escassez de medidas. ",],),
                            
                        ],
                        className="product",
                                style={"color": "#ffffff",
                                                "width": "100%",
                                                "verticalAlign": "top",
                                                "font-size":"150%"
                                        },
                        #className="row",
                    ),
                    
                ],
                className="sub_page",
            ),
        ],
        className="page",
    )
