import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import sqlite3
import os
from flask import g
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Función para obtener la conexión a la base de datos
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return db

# Ruta para la página principal
@app.route('/')
def index():
    return app.index()

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
        html.Button('Actualizar', id='submit-button', n_clicks=0)
    ]),
    html.Div([
        html.H2("Tabla de Datos"),
        dash_table.DataTable(id='data-table'),
        html.H2("Gráficas"),
        dcc.Graph(id='ph-graph'),
        dcc.Graph(id='turbidity-graph'),
        dcc.Graph(id='conductivity-graph'),
        dcc.Graph(id='temp-graph')
    ]),
    html.Div([
        html.H2("Agregar Datos"),
        dbc.Input(id='ph-input', type='number', placeholder='pH'),
        dbc.Input(id='turbidity-input', type='number', placeholder='Turbidez'),
        dbc.Input(id='conductivity-input', type='number', placeholder='Conductividad'),
        dbc.Input(id='temp-input', type='number', placeholder='Temperatura'),
        html.Button('Agregar', id='submit-button', n_clicks=0)
    ]),
    html.Div([
        html.H2("Eliminar Datos"),
        dash_table.DataTable(id='delete-table', editable=True),
        html.Button('Eliminar', id='delete-button', n_clicks=0)
    ])
])

# Actualizar datos de la tabla y gráficas
@app.callback(
    [Output('data-table', 'data'),
     Output('ph-graph', 'figure'),
     Output('turbidity-graph', 'figure'),
     Output('conductivity-graph', 'figure'),
     Output('temp-graph', 'figure')],
    [Input('submit-button', 'n_clicks'),
     Input('start-date', 'date'),
     Input('end-date', 'date')])
def update_data(n_clicks, start_date, end_date):
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'submit-button.n_clicks' and n_clicks > 0:
        # Obtener datos de la base de datos
        query = "SELECT * FROM mediciones WHERE fecha BETWEEN ? AND ?"
        df = pd.read_sql_query(query, get_db(), params=[start_date, end_date])

        # Generar gráficas
        ph_fig = px.line(df, x='fecha', y='ph')
        turbidity_fig = px.line(df, x='fecha', y='turbidez')
        conductivity_fig = px.line(df, x='fecha', y='conductividad')
        temp_fig = px.line(df, x='fecha', y='temperatura')

        # Actualizar tabla de datos
        return df.to_dict('records'), ph_fig, turbidity_fig, conductivity_fig, temp_fig
    else:
        return [], {}, {}, {}, {}

# Agregar nuevos datos
@app.callback(
    Output('data-table', 'data'),
    [Input('submit-button', 'n_clicks'),
     State('ph-input', 'value'),
     State('turbidity-input', 'value'),
     State('conductivity-input', 'value'),
     State('temp-input', 'value')])
def add_data(n_clicks, ph, turbidity, conductivity, temp):
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'submit-button.n_clicks' and n_clicks > 0:
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
        else:
            return dash.no_update
    else:
        return dash.no_update

# Eliminar datos
@app.callback(
    Output('data-table', 'data'),
    [Input('delete-button', 'n_clicks'),
     State('delete-table', 'data'),
     State('delete-table', 'selected_rows')])
def delete_data(delete_clicks, rows, selected_rows):
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'delete-button.n_clicks' and delete_clicks > 0:
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
    else:
        return dash.no_update

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run_server(host='0.0.0.0', port=port, debug=True)