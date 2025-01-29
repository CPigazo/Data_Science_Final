# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Define launch sites from the dataframe
launch_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create the options for the dropdown menu
options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=options,
        value='ALL',  # Default value
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # Pie chart for successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # Slider for payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,  # Adjust based on your data
        step=100,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[0, 10000],  # Default range
    ),

    # Scatter chart for payload vs launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for updating pie chart based on dropdown selection
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
    
    success_counts = filtered_df['class'].value_counts()
    fig = px.pie(
        names=success_counts.index,
        values=success_counts.values,
        title='Total Success Launches' if selected_site == 'ALL' else f'Success Launches for {selected_site}'
    )
    
    return fig

# Callback for updating scatter plot based on dropdown and slider
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter_plot(selected_site, payload_range):
    # Filter data based on selected payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    # Check if a specific site is selected or All
    if selected_site == 'ALL':
        filtered_df = filtered_df  # No additional filtering needed for all sites
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload vs Launch Outcome',
        labels={'class': 'Launch Outcome'},
        hover_name='Booster Version Category'
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
