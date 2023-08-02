# Importing Dash libraries
from dash import Dash, dcc, html, Input, Output
from StrawHouseAnalysis import StrawHouseAnalysis
import pandas as pd

# Creating the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

# Embedding the YouTube video
video_url = "https://www.youtube.com/embed/lHx9nDOaXIQ"
file_path = 'https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv'
data = pd.read_csv(file_path)

# Dropdown options for country selection
country_options = [{'label': country, 'value': country} for country in data['country'].unique()]

# LaTeX content for mathematical explanation
latex_content = r"""
\section{Estimating the Carbon Footprint Impact of Straw Houses}

Let's consider the following variables:
\begin{itemize}
    \item \( C \): Total carbon footprint from all sources.
    \item \( H \): Percentage of total carbon footprint caused by the housing industry.
    \item \( S \): Number of straw houses, assuming exponential growth from the selected starting year.
    \item \( R \): Reduction in carbon footprint per straw house.
    \item \( \text{{starting\_year}} \): The year from which the exponential growth in straw houses begins (default 1950).
    \item \( \text{{degradation\_rate}} \): The rate at which the carbon footprint reduction due to straw houses degrades over time.
    \item \( \text{{growth\_rate}} \): The exponential growth rate of straw houses.
\end{itemize}

The total carbon footprint contributed by the housing industry can be represented as:
\[
C_{\text{{housing}}} = C \times \frac{H}{100}
\]

The number of straw houses grows exponentially from the selected starting year:
\[
S = (\text{{year}} \geq \text{{starting\_year}}) \times \exp(\text{{growth\_rate}} \times (\text{{year}} - \text{{starting\_year}}))
\]

The degradation of the reduction effect of straw houses is applied as:
\[
S \times= (1 - \text{{degradation\_rate}})^{(\text{{year}} - \text{{starting\_year}})}
\]

The total reduction in carbon footprint due to straw houses can be represented as:
\[
C_{\text{{straw}}} = S \times R
\]

Therefore, the adjusted carbon footprint for the housing industry, considering the subtractive effect of straw houses, is:
\[
C_{\text{{adjusted}}} = C_{\text{{housing}}} - C_{\text{{straw}}} = C \times \frac{H}{100} - S \times R
\]

This equation helps in understanding the potential impact of building houses with straw, reflecting a temporary decrease in CO2 emissions, considering the exponential growth of straw houses and the degradation of the reduction effect over time.
"""

# Layout for the app
app.layout = html.Div([
    html.Script(src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"),
    dcc.Tabs(id='tabs', value='video-tab', children=[
        dcc.Tab(label='Video', value='video-tab'),
        dcc.Tab(label='Analysis', value='analysis-tab'),
        dcc.Tab(label='Math Explanation', value='math-tab')  # New Math Explanation Tab
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
        return html.Iframe(src=video_url, width="100%", height="500")
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
                value='United States',
                style={'display': 'none'}
            ),
            dcc.Slider(  # Decade Slider
                id='decade-slider',
                min=1950,
                max=2030,
                step=10,
                value=1950,
                marks={year: str(year) for year in range(1950, 2031, 10)}
            ),
            html.Div(id='slider-tooltip'),  # Tooltip for the Slider
            dcc.Graph(id='analysis-plot')
        ])
    elif selected_tab == 'math-tab':
        return html.Div([
            dcc.Markdown(latex_content, dangerously_allow_html=True)
        ])


@app.callback(
    Output('slider-tooltip', 'children'),
    [Input('decade-slider', 'value')]
)
def update_slider_tooltip(selected_year):
    return f"This is what the curves would look like if we had started in the year {selected_year}."


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
