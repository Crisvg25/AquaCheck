import dash
from dash import dcc, html
import pandas as pd
import os

# Leer el archivo CSV
df = pd.read_csv('datos_agua.csv')

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Importante: esto es necesario para Render
server = app.server

app.layout = html.Div(children=[
    html.H1(children='Monitoreo de la Calidad del Agua en La Ceja'),

    # Gráfico de pH
    dcc.Graph(
        id='ph-graph',
        figure={
            'data': [
                {'x': df['Fecha'] + ' ' + df['Hora'], 'y': df['pH'], 'type': 'line', 'name': 'pH'},
            ],
            'layout': {
                'title': 'Nivel de pH en el Agua'
            }
        }
    ),

    # Gráfico de Turbidez
    dcc.Graph(
        id='turbidez-graph',
        figure={
            'data': [
                {'x': df['Fecha'] + ' ' + df['Hora'], 'y': df['Turbidez'], 'type': 'line', 'name': 'Turbidez'},
            ],
            'layout': {
                'title': 'Turbidez del Agua'
            }
        }
    ),

    # Gráfico de Conductividad
    dcc.Graph(
        id='conductividad-graph',
        figure={
            'data': [
                {'x': df['Fecha'] + ' ' + df['Hora'], 'y': df['Conductividad'], 'type': 'line', 'name': 'Conductividad'},
            ],
            'layout': {
                'title': 'Conductividad del Agua'
            }
        }
    ),

    # Gráfico de Temperatura
    dcc.Graph(
        id='temperatura-graph',
        figure={
            'data': [
                {'x': df['Fecha'] + ' ' + df['Hora'], 'y': df['Temperatura'], 'type': 'line', 'name': 'Temperatura'},
            ],
            'layout': {
                'title': 'Temperatura del Agua'
            }
        }
    ),
])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run_server(host='0.0.0.0', port=port, debug=False)