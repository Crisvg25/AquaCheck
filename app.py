import pandas as pd
import sqlite3
import os
from flask import g
import dash
from dash import html, dcc  
import dash_table
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import logging

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # Obtén la conexión a la base de datos de las variables de entorno de Render
        db_path = os.environ.get('DATABASE_URL', 'agua.db')
        db = g._database = sqlite3.connect(db_path)
    return db

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

@server.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        logging.info("Conexión a la base de datos cerrada")

with app.server.app_context():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mediciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        hora TEXT,
        ph REAL,
        turbidez REAL,
        conductividad REAL,
        temperatura REAL
    )
    ''')
    db.commit()

app.layout = dbc.Container([
    html.H1("AquaCheck La Ceja", className="text-center my-4"),
    
    dbc.Row([
        dbc.Col([
            html.H3("Agregar nueva medición", className="mb-3 text-primary"),
            dbc.Form([
                dbc.Row([
                    dbc.Col(dbc.Input(id='fecha', type='date', placeholder='Fecha')),
                    dbc.Col(dbc.Input(id='hora', type='time', placeholder='Hora')),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(dbc.Input(id='ph', type='number', placeholder='pH')),
                    dbc.Col(dbc.Input(id='turbidez', type='number', placeholder='Turbidez')),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(dbc.Input(id='conductividad', type='number', placeholder='Conductividad')),
                    dbc.Col(dbc.Input(id='temperatura', type='number', placeholder='Temperatura')),
                ], className="mb-3"),
                dbc.Button('Agregar', id='submit-button', color="primary", className="mt-3"),
            ]),
        ], md=4),
        dbc.Col([
            html.H3("Filtrar datos", className="mb-3 text-primary"),
            dcc.DatePickerRange(
                id='date-range',
                start_date=datetime.now().date() - timedelta(days=30),
                end_date=datetime.now().date(),
                display_format='YYYY-MM-DD'
            ),
        ], md=8),
    ], className="mb-4"),
    
    html.H3("Datos ingresados", className="mb-3 text-primary"),
    dash_table.DataTable(
        id='table',
        columns=[
            {"name": i, "id": i} for i in ["id", "fecha", "hora", "ph", "turbidez", "conductividad", "temperatura"]
        ],
        page_size=10,
        style_table={'overflowX': 'auto'},
    ),
    dbc.Button('Eliminar seleccionados', id='delete-button', color="danger", className="mt-3"),
    
    dbc.Spinner(children=[
        dbc.Row([
            dbc.Col(dcc.Graph(id='ph-graph'), md=6),
            dbc.Col(dcc.Graph(id='turbidez-graph'), md=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id='conductividad-graph'), md=6),
            dbc.Col(dcc.Graph(id='temperatura-graph'), md=6),
        ]),
    ], color="primary", type="grow", fullscreen=True),
])

@app.callback(
    [Output('ph-graph', 'figure'),
     Output('turbidez-graph', 'figure'),
     Output('conductividad-graph', 'figure'),
     Output('temperatura-graph', 'figure'),
     Output('table', 'data')],
    [Input('submit-button', 'n_clicks'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('delete-button', 'n_clicks')],
    [State('fecha', 'value'), State('hora', 'value'),
     State('ph', 'value'), State('turbidez', 'value'),
     State('conductividad', 'value'), State('temperatura', 'value'),
     State('table', 'selected_rows')]
)
def update_data(n_clicks, start_date, end_date, delete_clicks, fecha, hora, ph, turbidez, conductividad, temperatura, selected_rows):
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'submit-button.n_clicks':
        if all([fecha, hora, ph, turbidez, conductividad, temperatura]):
            with app.server.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('''
                    INSERT INTO mediciones (fecha, hora, ph, turbidez, conductividad, temperatura)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (fecha, hora, ph, turbidez, conductividad, temperatura))
                db.commit()
                logging.info("Datos agregados a la base de datos")

    elif ctx.triggered[0]['prop_id'] == 'delete-button.n_clicks':
        if selected_rows:
            with app.server.app_context():
                db = get_db()
                cursor = db.cursor()
                for row in selected_rows:
                    cursor.execute("DELETE FROM mediciones WHERE id=?", (row,))
                db.commit()
                logging.info("Datos eliminados de la base de datos")

    with app.server.app_context():
        query = f"SELECT * FROM mediciones WHERE fecha BETWEEN '{start_date}' AND '{end_date}'"
        df = pd.read_sql_query(query, get_db())

    ph_fig = {
        'data': [
            {'x': df['fecha'] + ' ' + df['hora'], 'y': df['ph'], 'type': 'scatter', 'mode': 'lines+markers', 'name': 'pH'},
            {'x': df['fecha'] + ' ' + df['hora'], 'y': [6.5] * len(df), 'type': 'line', 'name': 'Límite inferior', 'line': {'dash': 'dash'}},
            {'x': df['fecha'] + ' ' + df['hora'], 'y': [9.0] * len(df), 'type': 'line', 'name': 'Límite superior', 'line': {'dash': 'dash'}}
        ],
        'layout': {
            'title': {'text': '<b>Nivel de pH en el Agua</b>', 'font': {'size': 24}},
            'yaxis': {'range': [0, 14]},
            'hovermode': 'closest'
        }
    }

    turbidez_fig = {
        'data': [
            {'x': df['fecha'] + ' ' + df['hora'], 'y': df['turbidez'], 'type': 'scatter', 'mode': 'lines+markers', 'name': 'Turbidez'},
            {'x': df['fecha'] + ' ' + df['hora'], 'y': [5] * len(df), 'type': 'line', 'name': 'Límite máximo', 'line': {'dash': 'dash'}}
        ],
        'layout': {
            'title': {'text': '<b>Turbidez del Agua</b>', 'font': {'size': 24}},
            'hovermode': 'closest'
        }
    }

    conductividad_fig = {
        'data': [
            {'x': df['fecha'] + ' ' + df['hora'], 'y': df['conductividad'], 'type': 'scatter', 'mode': 'lines+markers', 'name': 'Conductividad'},
            {'x': df['fecha'] + ' ' + df['hora'], 'y': [50] * len(df), 'type': 'line', 'name': 'Límite inferior', 'line': {'dash': 'dash'}},
            {'x': df['fecha'] + ' ' + df['hora'], 'y': [1000] * len(df), 'type': 'line', 'name': 'Límite superior', 'line': {'dash': 'dash'}}
        ],
        'layout': {
            'title': {'text': '<b>Conductividad del Agua</b>', 'font': {'size': 24}},
            'hovermode': 'closest'
        }
    }

    temperatura_fig = {
        'data': [
            {'x': df['fecha'] + ' ' + df['hora'], 'y': df['temperatura'], 'type': 'scatter', 'mode': 'lines+markers', 'name': 'Temperatura'},
            {'x': df['fecha'] + ' ' + df['hora'], 'y': [10] * len(df), 'type': 'line', 'name': 'Límite inferior', 'line': {'dash': 'dash'}},
            {'x': df['fecha'] + ' ' + df['hora'], 'y': [20] * len(df), 'type': 'line', 'name': 'Límite superior', 'line': {'dash': 'dash'}}
        ],
        'layout': {
            'title': {'text': '<b>Temperatura del Agua</b>', 'font': {'size': 24}},
            'hovermode': 'closest'
        }
    }

    return ph_fig, turbidez_fig, conductividad_fig, temperatura_fig, df.to_dict('records')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    logging.basicConfig(level=logging.INFO)
    app.run_server(host='0.0.0.0', port=port, debug=True)