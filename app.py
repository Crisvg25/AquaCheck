import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import sqlite3
import os
from flask import g

# Función para obtener la conexión a la base de datos
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('agua.db')
    return db

# Crear la aplicación Dash
app = dash.Dash(__name__)
server = app.server

# Configuración para cerrar la conexión después de cada solicitud
@server.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Crear la tabla si no existe
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

# ... (el resto del código de diseño de la aplicación permanece igual)

@app.callback(
    [Output('ph-graph', 'figure'),
     Output('turbidez-graph', 'figure'),
     Output('conductividad-graph', 'figure'),
     Output('temperatura-graph', 'figure')],
    [Input('submit-button', 'n_clicks')],
    [State('fecha', 'value'), State('hora', 'value'),
     State('ph', 'value'), State('turbidez', 'value'),
     State('conductividad', 'value'), State('temperatura', 'value')]
)
def update_graph(n_clicks, fecha, hora, ph, turbidez, conductividad, temperatura):
    if n_clicks > 0:
        if not all([fecha, hora, ph, turbidez, conductividad, temperatura]):
            return dash.no_update

        with app.server.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO mediciones (fecha, hora, ph, turbidez, conductividad, temperatura)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (fecha, hora, ph, turbidez, conductividad, temperatura))
            db.commit()

    # Leer los datos actualizados de la base de datos
    with app.server.app_context():
        df = pd.read_sql_query("SELECT * FROM mediciones", get_db())

    # ... (el resto del código para crear los gráficos permanece igual)

    return ph_fig, turbidez_graph, conductividad_fig, temperatura_fig

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run_server(host='0.0.0.0', port=port, debug=True)
