import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import os

# Leer el archivo CSV
df = pd.read_csv('datos_agua.csv')

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Importante: esto es necesario para Render
server = app.server

app.layout = html.Div(children=[
    html.H1(children='AquaCheck La Ceja'),

    # Formulario para agregar datos manualmente
    html.Div([
        html.H3("Agregar nueva medición"),
        dcc.Input(id='fecha', type='text', placeholder='Fecha (YYYY-MM-DD)'),
        dcc.Input(id='hora', type='text', placeholder='Hora (HH:MM)'),
        dcc.Input(id='ph', type='number', placeholder='pH'),
        dcc.Input(id='turbidez', type='number', placeholder='Turbidez'),
        dcc.Input(id='conductividad', type='number', placeholder='Conductividad'),
        dcc.Input(id='temperatura', type='number', placeholder='Temperatura'),
        html.Button('Agregar', id='submit-button', n_clicks=0)
    ]),

    # Gráficos de datos
    dcc.Graph(id='ph-graph'),
    dcc.Graph(id='turbidez-graph'),
    dcc.Graph(id='conductividad-graph'),
    dcc.Graph(id='temperatura-graph')
])

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
        # Verificar que los valores no sean None
        if not all([fecha, hora, ph, turbidez, conductividad, temperatura]):
            return dash.no_update  # No actualizar si falta algún valor

        # Agregar los nuevos datos al DataFrame
        new_data = {'Fecha': fecha, 'Hora': hora, 'pH': ph, 'Turbidez': turbidez,
                    'Conductividad': conductividad, 'Temperatura': temperatura}
        global df
        df = df.append(new_data, ignore_index=True)

        # Actualizar el archivo CSV con los nuevos datos
        df.to_csv('datos_agua.csv', index=False)

    # Crear gráficos actualizados
    ph_fig = {
        'data': [{'x': df['Fecha'] + ' ' + df['Hora'], 'y': df['pH'], 'type': 'line', 'name': 'pH'}],
        'layout': {'title': 'Nivel de pH en el Agua'}
    }

    turbidez_fig = {
        'data': [{'x': df['Fecha'] + ' ' + df['Hora'], 'y': df['Turbidez'], 'type': 'line', 'name': 'Turbidez'}],
        'layout': {'title': 'Turbidez del Agua'}
    }

    conductividad_fig = {
        'data': [{'x': df['Fecha'] + ' ' + df['Hora'], 'y': df['Conductividad'], 'type': 'line', 'name': 'Conductividad'}],
        'layout': {'title': 'Conductividad del Agua'}
    }

    temperatura_fig = {
        'data': [{'x': df['Fecha'] + ' ' + df['Hora'], 'y': df['Temperatura'], 'type': 'line', 'name': 'Temperatura'}],
        'layout': {'title': 'Temperatura del Agua'}
    }

    return ph_fig, turbidez_fig, conductividad_fig, temperatura_fig

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run_server(host='0.0.0.0', port=port, debug=True)

