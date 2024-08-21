import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import sqlite3
import os
from flask import g
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Función para obtener la conexión a la base de datos
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return db

# Diseño de la interfaz
app.layout = html.Div([
    html.H1("Monitoreo de Calidad de Agua"),
    html.Div([
        html.Label("Fecha inicio:"),
        dcc.DatePickerSingle(
            id='start-date',
            date=datetime.now().date() - timedelta(days=7)
        ),
        html.Label("Fecha fin:"),
        dcc.DatePickerSingle(
            id='end-date',
            date=datetime.now().date()
        ),
        html.Button('Actualizar', id='update-button', n_clicks=0)
    ]),
    html.Div([
        html.H2("Tabla de Datos"),
        dash_table.DataTable(
            id='data-table',
            columns=[
                {'name': 'ID', 'id': 'id'},
                {'name': 'pH', 'id': 'ph'},
                {'name': 'Turbidez', 'id': 'turbidez'},
                {'name': 'Conductividad', 'id': 'conductividad'},
                {'name': 'Temperatura', 'id': 'temperatura'},
                {'name': 'Fecha', 'id': 'fecha'}
            ],
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'border': '1px solid lightgrey'
            },
            style_data={
                'backgroundColor': 'white',
                'color': 'black'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(245, 245, 245)'
                }
            ]
        ),
        html.H2("Gráficas"),
        dcc.Graph(id='ph-graph', style={'height': '300px'}),
        dcc.Graph(id='turbidity-graph', style={'height': '300px'}),
        dcc.Graph(id='conductivity-graph', style={'height': '300px'}),
        dcc.Graph(id='temp-graph', style={'height': '300px'})
    ]),
    html.Div([
        html.H2("Agregar Datos"),
        dbc.Input(id='ph-input', type='number', placeholder='pH'),
        dbc.Input(id='turbidity-input', type='number', placeholder='Turbidez'),
        dbc.Input(id='conductivity-input', type='number', placeholder='Conductividad'),
        dbc.Input(id='temp-input', type='number', placeholder='Temperatura'),
        html.Button('Agregar', id='add-button', n_clicks=0)
    ]),
    html.Div([
        html.H2("Eliminar Datos"),
        dash_table.DataTable(
            id='delete-table',
            columns=[
                {'name': 'ID', 'id': 'id'},
                {'name': 'pH', 'id': 'ph'},
                {'name': 'Turbidez', 'id': 'turbidez'},
                {'name': 'Conductividad', 'id': 'conductividad'},
                {'name': 'Temperatura', 'id': 'temperatura'},
                {'name': 'Fecha', 'id': 'fecha'}
            ],
            editable=True
        ),
        html.Button('Eliminar', id='delete-button', n_clicks=0)
    ])
])

# Callback para actualizar datos de la tabla y gráficas
@app.callback(
    [Output('data-table', 'data'),
     Output('ph-graph', 'figure'),
     Output('turbidity-graph', 'figure'),
     Output('conductivity-graph', 'figure'),
     Output('temp-graph', 'figure')],
    [Input('update-button', 'n_clicks'),
     Input('start-date', 'date'),
     Input('end-date', 'date')]
)
def update_data(n_clicks, start_date, end_date):
    ctx = dash.callback_context
    if ctx.triggered and n_clicks > 0:
        # Obtener datos de la base de datos
        query = "SELECT * FROM mediciones WHERE fecha BETWEEN ? AND ?"
        df = pd.read_sql_query(query, get_db(), params=[start_date, end_date])

        # Generar gráficas con estilos personalizados
        ph_fig = px.line(df, x='fecha', y='ph', title='Gráfica de pH', 
                          labels={'ph': 'Valor de pH'}, 
                          template='plotly_white')
        ph_fig.update_layout(title_font=dict(size=20, color='black'), 
                             title_x=0.5, 
                             plot_bgcolor='rgba(0,0,0,0)', 
                             xaxis_title='Fecha',
                             yaxis_title='pH',
                             yaxis=dict(showgrid=True, gridcolor='lightgray'),
                             xaxis=dict(showgrid=True, gridcolor='lightgray'))

        turbidity_fig = px.line(df, x='fecha', y='turbidez', title='Gráfica de Turbidez', 
                                 labels={'turbidez': 'Turbidez (NTU)'}, 
                                 template='plotly_white')
        turbidity_fig.update_layout(title_font=dict(size=20, color='black'), 
                                     title_x=0.5,
                                     plot_bgcolor='rgba(0,0,0,0)', 
                                     xaxis_title='Fecha',
                                     yaxis_title='Turbidez',
                                     yaxis=dict(showgrid=True, gridcolor='lightgray'),
                                     xaxis=dict(showgrid=True, gridcolor='lightgray'))

        conductivity_fig = px.line(df, x='fecha', y='conductividad', title='Gráfica de Conductividad', 
                                    labels={'conductividad': 'Conductividad (µS/cm)'}, 
                                    template='plotly_white')
        conductivity_fig.update_layout(title_font=dict(size=20, color='black'), 
                                       title_x=0.5,
                                       plot_bgcolor='rgba(0,0,0,0)', 
                                       xaxis_title='Fecha',
                                       yaxis_title='Conductividad',
                                       yaxis=dict(showgrid=True, gridcolor='lightgray'),
                                       xaxis=dict(showgrid=True, gridcolor='lightgray'))

        temp_fig = px.line(df, x='fecha', y='temperatura', title='Gráfica de Temperatura', 
                            labels={'temperatura': 'Temperatura (°C)'}, 
                            template='plotly_white')
        temp_fig.update_layout(title_font=dict(size=20, color='black'), 
                               title_x=0.5,
                               plot_bgcolor='rgba(0,0,0,0)', 
                               xaxis_title='Fecha',
                               yaxis_title='Temperatura',
                               yaxis=dict(showgrid=True, gridcolor='lightgray'),
                               xaxis=dict(showgrid=True, gridcolor='lightgray'))

        # Actualizar tabla de datos
        return df.to_dict('records'), ph_fig, turbidity_fig, conductivity_fig, temp_fig
    else:
        return [], {}, {}, {}, {}

# Agregar nuevos datos
@app.callback(
    Output('data-table', 'data'),
    [Input('add-button', 'n_clicks'),
     State('ph-input', 'value'),
     State('turbidity-input', 'value'),
     State('conductivity-input', 'value'),
     State('temp-input', 'value')]
)
def add_data(n_clicks, ph, turbidity, conductivity, temp):
    ctx = dash.callback_context
    if ctx.triggered and n_clicks > 0:
        # Validar valores de entrada
        if (isinstance(ph, (int, float)) and isinstance(turbidity, (int, float)) and
            isinstance(conductivity, (int, float)) and isinstance(temp, (int, float))):
            # Insertar datos en la base de datos
            cur = get_db().cursor()
            cur.execute("INSERT INTO mediciones (ph, turbidez, conductividad, temperatura, fecha) VALUES (?, ?, ?, ?, ?)", 
                       (ph, turbidity, conductivity, temp, datetime.now().date()))
            get_db().commit()

            # Obtener los datos actualizados de la base de datos
            query = "SELECT * FROM mediciones"
            df = pd.read_sql_query(query, get_db())
            return df.to_dict('records')
    return dash.no_update

# Eliminar datos
@app.callback(
    Output('data-table', 'data'),
    [Input('delete-button', 'n_clicks'),
     State('delete-table', 'data'),
     State('delete-table', 'selected_rows')]
)
def delete_data(delete_clicks, rows, selected_rows):
    ctx = dash.callback_context
    if ctx.triggered and delete_clicks > 0:
        # Eliminar los datos seleccionados de la base de datos
        cur = get_db().cursor()
        for row_index in selected_rows:
            row = rows[row_index]
            cur.execute("DELETE FROM mediciones WHERE id = ?", (row['id'],))
        get_db().commit()

        # Obtener los datos actualizados de la base de datos
        query = "SELECT * FROM mediciones"
        df = pd.read_sql_query(query, get_db())
        return df.to_dict('records')
    return dash.no_update

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run_server(host='0.0.0.0', port=port, debug=True)
