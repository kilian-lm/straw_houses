# Importing Dash libraries
from dash import Dash, dcc, html, Input, Output
from StrawHouseAnalysis import StrawHouseAnalysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Creating the Dash app
app = Dash(__name__)

# Embedding the YouTube video
video_url = "https://www.youtube.com/embed/lHx9nDOaXIQ"
file_path = 'https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv'

data = pd.read_csv(file_path)


# Dropdown options for country selection
country_options = [{'label': country, 'value': country} for country in data['country'].unique()]

# Layout for the app
app.layout = html.Div([
    # Tabs for navigation
    dcc.Tabs(id='tabs', value='video-tab', children=[
        dcc.Tab(label='Video', value='video-tab'),
        dcc.Tab(label='Analysis', value='analysis-tab'),
    ]),
    # Content for the selected tab
    html.Div(id='tabs-content')
])


# Callback for updating the content based on the selected tab
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')]
)
def update_tab(selected_tab):
    if selected_tab == 'video-tab':
        # Embedding the YouTube video
        return html.Iframe(src=video_url, width="100%", height="500")
    elif selected_tab == 'analysis-tab':
        # Analysis tab with country selector and plot
        return html.Div([
            html.H3("Select Analysis Type:"),
            dcc.RadioItems(
                id='analysis-type',
                options=[
                    {'label': 'Global', 'value': 'global'},
                    {'label': 'By Country', 'value': 'by_country'},
                ],
                value='global',
                labelStyle={'display': 'block'}
            ),
            dcc.Dropdown(
                id='country-selector',
                options=country_options,
                value='United States',
                style={'display': 'none'}  # Hidden by default
            ),
            dcc.Graph(id='analysis-plot')  # Plot for the analysis
        ])


# Callback for updating the country selector visibility
@app.callback(
    Output('country-selector', 'style'),
    [Input('analysis-type', 'value')]
)
def update_country_selector(analysis_type):
    return {'display': 'block'} if analysis_type == 'by_country' else {'display': 'none'}


# Callback for updating the analysis plot
@app.callback(
    Output('analysis-plot', 'figure'),
    [Input('analysis-type', 'value'),
     Input('country-selector', 'value')]
)
def update_analysis_plot(analysis_type, selected_country):
    # Initializing the analysis class
    analysis = StrawHouseAnalysis(file_path, country=selected_country, by_country=(analysis_type == 'by_country'))

    # Performing the analysis and retrieving the data
    analysis_data = analysis._StrawHouseAnalysis__filter_and_calculate()

    # Creating the plot figure
    figure = {
        'data': [
            {'x': analysis_data['year'], 'y': analysis_data['C_housing'], 'type': 'line',
             'name': 'Original Carbon Footprint'},
            {'x': analysis_data['year'], 'y': analysis_data['C_straw'], 'type': 'line',
             'name': 'Reduction Due to Straw Houses'},
            {'x': analysis_data['year'], 'y': analysis_data['C_adjusted'], 'type': 'line',
             'name': 'Adjusted Carbon Footprint', 'line': {'dash': 'dash'}}
        ],
        'layout': {
            'title': 'Impact of Straw Houses on Carbon Footprint of Housing Industry',
            'xaxis': {'title': 'Year'},
            'yaxis': {'title': 'Carbon Footprint (Metric Tons CO2)'}
        }
    }

    return figure


# Running the app
if __name__ == '__main__':
    app.run_server(debug=True)
