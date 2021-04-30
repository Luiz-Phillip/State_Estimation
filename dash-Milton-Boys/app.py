# -*- coding: utf-8 -*-
import dash
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash_table.Format import Format
from dash.dependencies import Input, Output, State
from utils import make_dash_table, MountJSon
from PSSS import state_estimation, observable_system
import base64
import pandas as pd
import io
import os
import urllib as urllib
import json
from pages import (
    overview,
    pricePerformance,
    portfolioManagement,
    feesMins,
    distributions,
    newsReviews,
)
import webbrowser as web
#ToDo: browser




m_Table=pd.DataFrame()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], suppress_callback_exceptions=True
)
server = app.server

# Describe the layout/ UI of the app
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

# Update page
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/dash/state-estimation":
        return pricePerformance.create_layout(app)
    elif pathname == "/dash-financial-report/portfolio-management":
        return portfolioManagement.create_layout(app)
    elif pathname == "/dash-financial-report/fees":
        return feesMins.create_layout(app)
    elif pathname == "/dash-financial-report/distributions":
        return distributions.create_layout(app)
    elif pathname == "/dash-financial-report/news-and-reviews":
        return newsReviews.create_layout(app)
    elif pathname == "/dash-financial-report/full-view":
        return (
            overview.create_layout(app),
            pricePerformance.create_layout(app),
            portfolioManagement.create_layout(app),
            feesMins.create_layout(app),
            distributions.create_layout(app),
            newsReviews.create_layout(app),
        )
    else:
        return overview.create_layout(app)



@app.callback([Output("topology_table", "data"), Output("topology_table", "columns")], [Input('topology', 'contents')], [State('topology', 'filename')])
def update_topology(contents, filename):
    if not contents:
        return  [{" ":" "}], [{"name": " ", "id": " "}]
    else:
        dff, _ = parse_contents(contents, filename)
        return dff.to_dict('records'), [{"name": i, "id": i, "format": Format(precision = 4)} for i in dff.columns]

@app.callback([Output('intermediate-value', 'children'), Output('input-se-top', 'children')], Input('topology_table', 'data'), Input('topology_table', 'columns'))
def topology_se(rows, columns):
    if len(rows) < 2:
        b=json.dumps({})
        return json.dumps({}), json.dumps({})
    else:
        df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
        REDE = MountJSon(df)
        return json.dumps({'topology':REDE}), json.dumps({'data': df.to_json(orient='split', date_format='iso')})

@app.callback(Output('cytoscape', 'elements'), Input('intermediate-value', 'children'))
def update_graph(network):
    if len(network) > 2:
        return json.loads(network).get('topology')
    else:
        return {}

###########Reading Meas Data#############
@app.callback([Output("meansured_table", "data"), Output("meansured_table", "columns"),Output(component_id="meansured_table", component_property="selected_rows")], [Input('meansured', 'contents')],
    [State('meansured', 'filename')])
def update_meansured(contents, filename):
    if not contents:
        return  [{" ":" "}], [{"name": " ", "id": " "}],[]
    if contents:
        global m_Table
        dff, _= parse_contents(contents, filename, is_topology = False)
        m_Table=dff
        n=dff.shape[0]
        return dff.to_dict('records'), [{"name": i, "id": i} for i in dff.columns],list(range(n))

@app.callback([Output('input-se-med', 'children')], [Input("meansured_table", 'data'), Input("meansured_table", 'columns'),Input("meansured_table", 'selected_rows')])
def meas_se(rows, columns,selected_rows):
    if len(rows) < 2:
        return [json.dumps({})]
    else:
        # df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
        # df=df[df.index.isin(selected_rows)]
        df=m_Table[m_Table.index.isin(selected_rows)]
        df.dropna(inplace=True)
        return [json.dumps({'data': df.to_json(orient='split', date_format='iso')})]

@app.callback([Output("output_state", "children"), Output("output_med", "children"),Output("graph","figure"),Output("criticalities", "data"), Output("criticalities", "columns")], [Input('input-se-top', 'children'), Input('input-se-med', 'children')])
#Saídas->>> y_bus_matrix, criticality_data, J_list, J_critical, State_dataframe, data_SE
def update_se(topology, meansured):
    if len(topology) > 2 and len(meansured) > 2:
        data_1, data_2 = json.loads(topology), json.loads(meansured)
        line = pd.read_json(data_1['data'], orient='split')
        med = pd.read_json(data_2['data'], orient='split')
        is_observable, _ = observable_system(meansured_data_instante=med, line_data=line)
        if is_observable:
            _, criticality_data, J_list,J_critical, State_dataframe, data_SE,is_observable = state_estimation(meansured_data_instante=med, line_data=line)
            criticality_data= criticality_data.dropna().sort_values(by= 'Cricality')
            criticality_data= criticality_data.astype({"Location": str})
            fig = px.line(x=range(1,len(J_list)+1),y=J_list,log_y=True,title="Objective Function (J(x))",labels=dict(x='Iterations',y='log(J(x))'))
            # print(J_critical)
            fig.add_hline(y=J_critical, line_width=3, line_dash="dash", line_color="green")
            return json.dumps({'data': State_dataframe.to_json(orient='split', date_format='iso')}), json.dumps({'data': data_SE.to_json(orient='split', date_format='iso')}),fig, criticality_data.to_dict('records'), [{"name": i, "id": i} for i in  criticality_data.columns]
        else:
            return json.dumps({}), json.dumps({}),{},[{" ":" "}], [{"name": " ", "id": " "}]    
    else:
        # return html.Div(style={'display': 'none'}), html.Div(style={'display': 'none'})
        return json.dumps({}), json.dumps({}),{},[{" ":" "}], [{"name": " ", "id": " "}]

###############################################Print Tabela dos Estados Estimados###############################################
@app.callback(Output("se_table", "data"),Output("se_table", "columns"), [Input('output_state', 'children')])
def update_se_table(estimated_state):
    if len(estimated_state) > 2:
        data_1 = json.loads(estimated_state)
        State_dataframe = pd.read_json(data_1['data'], orient='split')
        return State_dataframe.to_dict('records'), [{"name": i, "id": i} for i in State_dataframe.columns]
    else:
        return [{" ":" "}], [{"name": " ", "id": " "}]

###############################################Print Tabela das Medidas Estimadas###############################################
@app.callback(Output("se_meansured_table", "data"),Output("se_meansured_table", "columns"), [Input('output_med', 'children')])
def update_se_med(med):
    if len(med) > 2:
        data_1 = json.loads(med)
        State_dataframe1 = pd.read_json(data_1['data'], orient='split')
        State_dataframe1= State_dataframe1.astype({"Location": str})
        return State_dataframe1.to_dict('records'), [{"name": i, "id": i} for i in State_dataframe1.columns]
        #return make_dash_table(State_dataframe) 
    else:
        return [{" ":" "}], [{"name": " ", "id": " "}]


def parse_contents(contents, filename, is_topology = True):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv( io.StringIO(decoded.decode('utf-8')), sep = ';')
    elif 'xls' in filename:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded))
    columns_selected = [x for x in df.columns if "Unn" not in x]
    network = MountJSon(df) if is_topology else {}
    return df[columns_selected], network

######################################################Interação com o Grafo#####################################################
def getTitle(sed, snd):
    if (sed or snd):
        # print(snd)
        # print(sed)
        ans = ""
        if (sed != [] and snd != []) or (sed == [] and snd == []):
            return ("Properties")
        if snd != []:
            nodes = []
            for i in snd:
                nodes.append(i['id'])
            if len(nodes) > 1:
                ans = "Properties of the Buses " 
            else:
                ans = "Properties of the Bus " + nodes[0]
                return (ans)
            for i in range(len(nodes) - 1):
                ans = ans + nodes[i] + ", "
            ans = ans + "and " + nodes[-1]
            return (ans)
        else:
            branches = []
            for i in sed:
                branches.append(i['source'] + '-' + i['target'])
            if len(branches) > 1:
                ans = "Properties of the Branches " 
            else:
                ans = "Properties of the Branch " + branches[0]
                return (ans)
            for i in range(len(branches) - 1):
                ans = ans + branches[i] + ", "
            ans = ans + "and " + branches[-1]
            return (ans)
    else:
        return ("Properties")

@app.callback(
    Output('properites-title', 'children'),
    Input('cytoscape', 'selectedEdgeData'),
    Input('cytoscape', 'selectedNodeData')
)
def updatePropertiesTitle(sed, snd):
    return html.H6(getTitle(sed, snd))

# measurement data utils
def getMeasLine(data, de, para, tipo):
    for i in range(len(data)):
        if data[i]['Para'] == para and data[i]['De'] == de and data[i]['Tipo'] == tipo:
            return i
    return -1

## Branch
def getBranchMeasLines(data, de, para):
    return [getMeasLine(data, de, para, 'P'), getMeasLine(data, de, para, 'Q'), getMeasLine(data, para, de, 'P'), getMeasLine(data, para, de, 'Q')]

def getBranchValues(data, de, para):
    lines = getBranchMeasLines(data, de, para)
    return [data[i]['Valor'] if i!=-1 else '' for i in lines]

def getBranchStdDevs(data, de, para):
    lines = getBranchMeasLines(data, de, para)
    return [data[i]['Desvio_Pad'] if i!=-1 else '' for i in lines]

def getSelectedBranchMeas(data, de, para, selectedMeasurementTable):
    ans = []
    for i in getBranchMeasLines(data, de, para):
        if i in selectedMeasurementTable:
            if data[i]['Tipo'] == 'P':
                if data[i]['De'] == de:
                    ans.append(0)   
                elif data[i]['Para'] == de:
                    ans.append(2)
            elif data[i]['Tipo'] == 'Q':
                if data[i]['De'] == de:
                    ans.append(1)
                elif data[i]['Para'] == de:
                    ans.append(3)
    return sorted(ans)

## Bus
def getBusMeasLines(data, bus):
    return [getMeasLine(data, bus, '-', 'P'), getMeasLine(data, bus, '-', 'Q'), getMeasLine(data, bus, '-', 'V')]

def getBusValues(data, bus):
    lines = getBusMeasLines(data, bus)
    return [data[i]['Valor'] for i in lines]

def getBusStdDevs(data, bus):
    lines = getBusMeasLines(data, bus)
    return [data[i]['Desvio_Pad'] for i in lines]

def getSelectedBusMeas(data, bus, selectedMeasurementTable):
    ans = []
    for i in getBusMeasLines(data, bus):
        if i in selectedMeasurementTable:
            if data[i]['Tipo'] == 'P':
                ans.append(0)
            elif data[i]['Tipo'] == 'Q':
                ans.append(1)
            elif data[i]['Tipo'] == 'V':
                ans.append(2)
    return sorted(ans)

@app.callback(
    [Output('chkMeasurements', 'data'),
     Output('chkMeasurements', 'columns'),
     Output('chkMeasurements', 'selected_rows')],
    Input('cytoscape', 'selectedEdgeData'),
    Input('cytoscape', 'selectedNodeData'),
    Input('meansured_table', 'data'),
    Input('meansured_table', 'selected_rows')
)
def updatePropertiesMeaChkList(sed, snd, data, selectedMeasurementTable):
    ans = []
    selected = []
    if (sed != [] and snd != []) or (sed == [] and snd == []):
        ans = [] # do nothing
    elif snd != []:
        labels = ['Active Power Injection', 'Reactive Power Injection', 'Voltage Magnitude']
        if len(snd) == 1:
            selected = getSelectedBusMeas(data, int(snd[0]['id']), selectedMeasurementTable)
            values = getBusValues(data, int(snd[0]['id']))
            stdDevs = getBusStdDevs(data, int(snd[0]['id']))
            ans = [{'Measurement': i, 'Value': j, 'Standard Deviation': k} for i, j, k in zip(labels, values, stdDevs)]
        else:
            ans = [{'Measurement': i, 'Value': '-', 'Standard Deviation': '-'} for i in labels]
    else:
        labels = ['Active Power Flow to-from', 'Reactive Power Flow to-from', 'Active Power Flow from-to', 'Reactive Power Flow from-to']
        if len(sed) == 1:
            selected = getSelectedBranchMeas(data, int(sed[0]['source']), int(sed[0]['target']), selectedMeasurementTable)
            values = getBranchValues(data, int(sed[0]['source']), int(sed[0]['target']))
            stdDevs = getBranchStdDevs(data, int(sed[0]['source']), int(sed[0]['target']))
            ans = [{'Measurement': i, 'Value': j, 'Standard Deviation': k} for i, j, k in zip(labels, values, stdDevs)]
        else:
            ans = [{'Measurement': i, 'Value': '-', 'Standard Deviation': '-'} for i in labels]
    return ans, [{'name': i, 'id': i} for i in ['Measurement', 'Value', 'Standard Deviation'] if ans != []], selected

# @app.callback(
#     Output('meansured_table', 'selected_rows'),
#     Input('meansured_table', 'data'),
#     Input('btn-savePropertiesChanges', 'n_clicks'),
#     State('meansured_table','selected_rows'),
#     State('chkMeasurements', 'selected_rows')
# )
# def saveChangesMeaChkList(data, n_clicks, selectedMeasurementTable, selectedProperties):
#     ans = getSelectedBusMeas(data, bus, selectedMeasurementTable)
#     return ans



# def getBusMeasurementData(busNo, data, labels):
#     values = [''] * len(labels)
#     std_dev = [''] * len(labels)
#     tableLine = [''] * len(labels)
#     for i in range(len(data)):
#         if data[i]['Para'] == '-' and data[i]['De'] == str(busNo):
#             if data[i]['Tipo'] == 'P':
#                 values[0] = data[i]['Valor']
#                 std_dev[0] = data[i]['Desvio_Pad']
#                 tableLine[0] = i
#                 continue
#             elif data[i]['Tipo'] == 'Q':
#                 values[2] = data[i]['Valor']
#                 std_dev[2] = data[i]['Desvio_Pad']
#                 tableLine[2] = i
#                 continue
#             elif data[i]['Tipo'] == 'V':
#                 values[3] = data[i]['Valor']
#                 std_dev[3] = data[i]['Desvio_Pad']
#                 tableLine[3] = i
#                 continue
#     return values, std_dev, tableLine

# def getBusesMeasurementLines(busesNo, data, labels):
#     tableLines = ([''] * len(labels)) * len(busNo)
#     for i in range(len(busNo)):
#         _, _, tableLines[i] = getBusMeasurementData(busNo, data, labels)
#     return tableLines

# def getBranchMeasurementData(busFrom, busTo, data, labels):
#     values = [''] * len(labels)
#     std_dev = [''] * len(labels)
#     tableLine = [''] * len(labels)
#     for i in range(len(data)):
#         if data[i]['Para'] == '-' and data[i]['De'] == str(busNo):
#             if data[i]['Tipo'] == 'P':
#                 values[0] = data[i]['Valor']
#                 std_dev[0] = data[i]['Desvio_Pad']
#                 tableLine[0] = i
#                 continue
#             elif data[i]['Tipo'] == 'Q':
#                 values[2] = data[i]['Valor']
#                 std_dev[2] = data[i]['Desvio_Pad']
#                 tableLine[2] = i
#                 continue
#             elif data[i]['Tipo'] == 'V':
#                 values[3] = data[i]['Valor']
#                 std_dev[3] = data[i]['Desvio_Pad']
#                 tableLine[3] = i
#                 continue
#     return values, std_dev, tableLine

# @app.callback(
#     dash.dependencies.Output('meansured_table', 'data'),
#     [dash.dependencies.Input('container-button-basic', 'n_clicks'),
#     dash.dependencies.Input("meansured_table", "columns"),
#     dash.dependencies.Input("meansured_table", "data")],
#     [dash.dependencies.State('chkMeasurements', 'value')]
#     )
# def savePreferences(n_clicks, columns, data, value):
#     return 

###################################################################################################################

if __name__ == "__main__": 
    # web.open_new_tab('http://127.0.0.1:8050')
    os.system("start \"\" http://127.0.0.1:8050")
    app.run_server(debug=True)
    # urllib.request.urlopen('http://127.0.0.1:8050')
