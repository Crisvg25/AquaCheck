import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

# Leer el archivo CSV
df = pd.read_csv('datos_agua.csv')

# Crear la aplicación Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Monitoreo de la Calidad del Agua'),

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
    app.run_server(debug=True)

