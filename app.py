# Importing Dash libraries
from dash import Dash, dcc, html, Input, Output
from StrawHouseAnalysis import StrawHouseAnalysis
import pandas as pd
from flask import Flask
# Creating the Dash app

# server = Flask(__name__)

server = Flask(__name__)
app = Dash(server=server,  suppress_callback_exceptions=True)


# app = Dash(__name__, suppress_callback_exceptions=True)

# Embedding the YouTube video
video_url = "https://www.youtube.com/embed/lHx9nDOaXIQ"
file_path = 'https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv'
data = pd.read_csv("local_test.csv")
# data.info()
# data.to_csv("local_test.csv")

pdf_url = "/assets/math_expl.pdf"  # Replace with the path to your PDF file

# Dropdown options for country selection
country_options = [{'label': country, 'value': country} for country in data['country'].unique()]

# Layout for the app
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='video-tab', children=[
        dcc.Tab(label='Video', value='video-tab'),
        dcc.Tab(label='Analysis', value='analysis-tab'),
        dcc.Tab(label='Math Explanation', value='math-tab')
    ]),
    html.Div(id='tabs-content')
])

# Callback for updating the content based on the selected tab
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')]
)
def update_tab(selected_tab):
    if selected_tab == 'video-tab':
        return html.Iframe(src=video_url, width="100%", height="900")
    elif selected_tab == 'analysis-tab':
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
                value='Germany',
                style={'display': 'none'}
            ),
            dcc.Slider(
                id='decade-slider',
                min=1950,
                max=2030,
                step=10,
                value=1950,
                marks={year: str(year) for year in range(1950, 2031, 10)}
            ),
            html.Div(id='slider-tooltip'),
            dcc.Graph(id='analysis-plot')
        ])
    elif selected_tab == 'math-tab':
        return html.Iframe(src=pdf_url, width="100%", height="900")

# Callback for updating the country selector visibility
@app.callback(
    Output('country-selector', 'style'),
    [Input('analysis-type', 'value')]
)
def update_country_selector(analysis_type):
    return {'display': 'block'} if analysis_type == 'by_country' else {'display': 'none'}

# Callback for updating the tooltip of the slider
@app.callback(
    Output('slider-tooltip', 'children'),
    [Input('decade-slider', 'value')]
)
def update_slider_tooltip(selected_year):
    return f"This is what the curves would look like if we had started in the year {selected_year}."

# Callback for updating the analysis plot
@app.callback(
    Output('analysis-plot', 'figure'),
    [Input('analysis-type', 'value'),
     Input('country-selector', 'value'),
     Input('decade-slider', 'value')]
)
def update_analysis_plot(analysis_type, selected_country, starting_year):
    analysis = StrawHouseAnalysis(file_path, country=selected_country, by_country=(analysis_type == 'by_country'),
                                  starting_year=starting_year)
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

# Route handling
@server.route("/")
def MyDashApp():
    return app.index()

# Running the app
if __name__ == '__main__':
    app.run_server()



# if __name__ == '__main__':
#     import os
#     app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
#
