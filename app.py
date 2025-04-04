import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import numpy as np
import dash_bootstrap_components as dbc


my_app = dash.Dash('My app')
my_app.layout = html.Div([html.H1(children='Gonorrhea and Chlamydia Analysis',
                                  style={'textAlign':'center'}),

                          html.Br(),
                          dcc.Tabs(id = 'tabs',
                                   children=[
                                       dcc.Tab(label='Data Overview',value='t1'),
                                       dcc.Tab(label='Outlier Detection and Removal',value='t2'),

                                       dcc.Tab(label='Analysis between variables using Plots', value='t3'),
                                        dcc.Tab(label='Choropleth Map', value='t4'),
                                       dcc.Tab(label='Pie Charts', value='t5'),
                                       dcc.Tab(label='Temporal trend plots',value='t6'),


                                   ]
                                   ),
                          html.Div(id='layout')

]
)

df=pd.read_csv('preprocessed_data.csv')

from dash import dash_table
from dash import ctx


tab1_layout=html.Div([
            dash_table.DataTable(
                data=df.head(10).to_dict('records'),  # Display top 10 rows
                columns=[{'name': i, 'id': i} for i in df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
            ),
            html.Br(),
            html.Button("Download Dataset", id="btn_csv"),
            dcc.Download(id="download-dataframe-csv")
        ])

# Callback for downloading the CSV file
@my_app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(n_clicks):
    return dcc.send_data_frame(df.to_csv, "gonorrhea_chlamydia_data.csv")
df1=pd.read_csv('preprocessed_data.csv')
df2=df1.copy(deep=True)
numerical_columns = ['Cases','Rate per 100000']



tab2_layout = html.Div([
    html.H2("Outlier Detection and Removal", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select a numerical column:"),
        dcc.Dropdown(
            id='column-dropdown',
            options=[{'label': col, 'value': col} for col in numerical_columns],
            value=numerical_columns[0],  # Default value
            clearable=False
        ),
    ], style={'marginBottom': 30}),

    html.Div([
        dcc.RadioItems(
            id='plot-type',
            options=[
                {'label': 'Box Plot', 'value': 'boxplot'},
                {'label': 'Histogram', 'value': 'histogram'},
            ],
            value='boxplot',  # Default value
            labelStyle={'display': 'inline-block', 'marginRight': '10px'}
        ),
    ], style={'marginBottom': 30}),

    html.Div(id='plot-container')
])
for selected_column in numerical_columns:
    q1 = np.percentile(df2[selected_column], 25)
    q3 = np.percentile(df2[selected_column], 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Filter out outliers
    cleaned_df = df2[(df1[selected_column] >= lower_bound) & (df2[selected_column] <= upper_bound)]
@my_app.callback(
    Output('plot-container', 'children'),
    [Input('column-dropdown', 'value'),
     Input('plot-type', 'value')]
)
def update_plot(selected_column, plot_type):
    # Apply IQR outlier removal method to the selected column


    # Create the appropriate plot based on the selected plot type
    if plot_type == 'boxplot':
        fig_before = px.box(df2, y=selected_column)
        fig_before.update_layout(title=dict(text=f'Box Plot - Before Outlier Removal', y=0.95, x=0.5))
        fig_after = px.box(cleaned_df, y=selected_column)
        fig_after.update_layout(title=dict(text=f'Box Plot - After Outlier Removal', y=0.95, x=0.5))
    elif plot_type == 'histogram':
        fig_before = px.histogram(df2, x=selected_column)
        fig_before.update_layout(title=dict(text=f'Histogram - Before Outlier Removal', y=0.95, x=0.5))
        fig_after = px.histogram(cleaned_df, x=selected_column)
        fig_after.update_layout(title=dict(text=f'Histogram - After Outlier Removal', y=0.95, x=0.5))

    return html.Div([
        dcc.Graph(figure=fig_before),
        dcc.Graph(figure=fig_after)
    ])
# Define variables
continuous = ['Cases','Rate per 100000']
discrete = ['Race/Ethnicity','Sex','Age Group']

tab3_layout=html.Div([
    html.H1('Plots to show relationship between different variables in the dataset', style={'textAlign': 'center', 'margin-bottom': '20px'}),
    html.Div([
        html.H3('Select the continuous variable:', style={'margin-bottom': '10px'}),
        dcc.Dropdown(id='continuous-dropdown',
                     options=[{'label': i, 'value': i} for i in continuous],
                     placeholder='Select the continuous variable',
                     style={'width': '50%', 'margin': 'auto'}),
        html.Br(),
        html.H3('Select the discrete or categorical variable:', style={'margin-bottom': '10px'}),
        dcc.Dropdown(id='discrete-dropdown',
                     options=[{'label': i, 'value': i} for i in discrete],
                     placeholder='Select the discrete variable',
                     style={'width': '50%', 'margin': 'auto'}),
        html.Br(),
        html.H3('Select the plot type:', style={'margin-bottom': '10px'}),
        dcc.RadioItems(
            id="plot-type",
            value="Box Plot",
            options=["Box Plot", 'Violin Plot', 'Histogram Plot'],
            labelStyle={'display': 'block', 'margin-bottom': '10px'}
        ),
        html.Div([
            html.Label('Include indicator?', style={'margin-bottom': '10px'}),
            dcc.Checklist(
                id='hue-checkbox',
                options=[
                    {'label': 'Yes', 'value': 'include-hue'},
                ],
                value=[],
                style={'margin': 'auto'}
            ),
        ]),
        html.Br(),
        dcc.Graph(id='graph-3'),
    ], style={'width': '80%', 'margin': 'auto', 'border': '1px solid #ddd', 'padding': '20px', 'border-radius': '10px'}),
])

# Define callback to update the graph
@my_app.callback(
    Output('graph-3', 'figure'),
    [Input('continuous-dropdown', 'value'),
     Input('discrete-dropdown', 'value'),
     Input('plot-type', 'value'),
     Input('hue-checkbox', 'value')]
)
def update_bar_chart(continuous_var, discrete_var, plot_type, hue_checkbox):
    hue = None
    if 'include-hue' in hue_checkbox:
        hue = 'Indicator'

    if plot_type == 'Box Plot':
        fig = px.box(cleaned_df, x=discrete_var, y=continuous_var, color=hue)
    elif plot_type == 'Violin Plot':
        fig = px.violin(cleaned_df, x=discrete_var, y=continuous_var, color=hue)
    elif plot_type == 'Histogram Plot':
        fig = px.histogram(cleaned_df, x=discrete_var, y=continuous_var, color=hue)


    fig.update_layout(title=dict(text=f'{plot_type} between {continuous_var} and {discrete_var}', y=0.95, x=0.5))
    return fig

state_abbrev = {
    1: 'AL', 2: 'AK', 4: 'AZ', 5: 'AR', 6: 'CA', 8: 'CO', 9: 'CT', 10: 'DE', 11: 'DC', 12: 'FL',
    13: 'GA', 15: 'HI', 16: 'ID', 17: 'IL', 18: 'IN', 19: 'IA', 20: 'KS', 21: 'KY', 22: 'LA',
    23: 'ME', 24: 'MD', 25: 'MA', 26: 'MI', 27: 'MN', 28: 'MS', 29: 'MO', 30: 'MT', 31: 'NE',
    32: 'NV', 33: 'NH', 34: 'NJ', 35: 'NM', 36: 'NY', 37: 'NC', 38: 'ND', 39: 'OH', 40: 'OK',
    41: 'OR', 42: 'PA', 44: 'RI', 45: 'SC', 46: 'SD', 47: 'TN', 48: 'TX', 49: 'UT', 50: 'VT',
    51: 'VA', 53: 'WA', 54: 'WV', 55: 'WI', 56: 'WY'
}

# Map FIPS to State Abbreviation
df['State'] = df['FIPS'].map(state_abbrev)

# Group by state and indicator
geo_df = df.groupby(['State', 'Indicator']).agg({
    'Cases': 'mean',
    'Rate per 100000': 'mean'
}).reset_index()

numerical_columns = ['Cases', 'Rate per 100000']
# Initial default values
default_indicator = geo_df['Indicator'].unique()[0]
default_variable = numerical_columns[1]

# App layout
tab4_layout = html.Div([
    html.Label('Select Disease:'),
    dcc.Dropdown(
        id='indicator-dropdown',
        options=[{'label': ind, 'value': ind} for ind in geo_df['Indicator'].unique()],
        value=default_indicator
    ),

    html.Label('Select Variable:'),
    dcc.Dropdown(
        id='variable-dropdown',
        options=[{'label': var, 'value': var} for var in numerical_columns],
        value=default_variable
    ),

    dcc.Graph(id='choropleth-map', style={'width': '100%', 'height': '600px'}),

    html.Label('Select color bar range:'),
    dcc.RangeSlider(
        id='color-range-slider',
        min=0,
        max=100,
        step=1,
        marks={i: str(i) for i in range(0, 101, 10)},
        value=[0, 100]
    ),
])

# Callback function to update choropleth map
@my_app.callback(
    Output('choropleth-map', 'figure'),
    [
        Input('indicator-dropdown', 'value'),
        Input('variable-dropdown', 'value'),
        Input('color-range-slider', 'value')
    ]
)
def update_choropleth(indicator, variable, color_range):
    sub_df = geo_df[geo_df['Indicator'] == indicator]

    fig = px.choropleth(
        sub_df,
        locations='State',
        locationmode='USA-states',
        color=variable,
        scope='usa',
        color_continuous_scale='Reds',
        range_color=color_range,
        labels={variable: variable},
        title=f'{indicator} - {variable} by State'
    )
    return fig

import plotly.express as px
import plotly.graph_objects as go

tab5_layout = html.Div([
    html.Label('Select Disease:'),
    dcc.Dropdown(
        id='disease-dropdown-tab5',
        options=[{'label': d, 'value': d} for d in df['Indicator'].unique()],
        value=df['Indicator'].unique()[0],
        style={'marginBottom': '10px'}
    ),

    html.Label('Select Demographic Dimensions:'),
    dcc.Dropdown(
        id='demographic-multiselect-tab5',
        options=[
            {'label': 'Race/Ethnicity', 'value': 'Race/Ethnicity'},
            {'label': 'Age Group', 'value': 'Age Group'},
            {'label': 'Sex', 'value': 'Sex'}
        ],
        value=['Race/Ethnicity'],  # default selection
        multi=True,
        style={'marginBottom': '20px'}
    ),

    html.Div(id='multi-demographic-pie-charts')
])


@my_app.callback(
    Output('multi-demographic-pie-charts', 'children'),
    [Input('disease-dropdown-tab5', 'value'),
     Input('demographic-multiselect-tab5', 'value')]
)
def update_multiple_pies(disease, demographics):
    figs = []
    filtered_df = df[df['Indicator'] == disease]

    for demo in demographics:
        grouped_data = filtered_df.groupby(demo)['Cases'].sum().reset_index()
        fig = px.pie(
            grouped_data,
            names=demo,
            values='Cases',
            title=f'{disease} – {demo}',
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')

        # Adjust width dynamically
        chart_width = '48%' if demo == 'Race/Ethnicity' else '32%'

        figs.append(dcc.Graph(
            figure=fig,
            style={'display': 'inline-block', 'width': chart_width, 'height': '600px'}
        ))

    return figs

tab6_layout = html.Div([
    daq.BooleanSwitch(
        id='yaxis-switch-tab6',
        on=True,  # True = 'Rate per 100000', False = 'Cases'
        label='Cases | Rate per 100,000',
        labelPosition='top',
        style={'marginBottom': '20px'}
    ),

    dcc.Graph(id='temporal-line-chart', style={'width': '100%', 'height': '600px'})
])
@my_app.callback(
    Output('temporal-line-chart', 'figure'),
    [Input('yaxis-switch-tab6', 'on')]
)
def update_temporal_plot(toggle_state):
    y_variable = 'Rate per 100000' if toggle_state else 'Cases'
    grouped_df = df.groupby(['Year', 'Indicator'])[y_variable].mean().reset_index()

    fig = px.line(
        grouped_df,
        x='Year',
        y=y_variable,
        color='Indicator',
        title=f'Temporal Trend: Average {y_variable} by Disease Over Time',
        markers=True
    )
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title=y_variable,
        legend_title='Disease',
        hovermode='x unified'
    )
    return fig





@my_app.callback(
    Output(component_id='layout',component_property='children'),
    Input(component_id='tabs',component_property='value')
)
def update_layout(tabs):
    if tabs=='t1':
        return tab1_layout
    if tabs=='t2':
        return tab2_layout
    if tabs=='t3':
        return tab3_layout
    if tabs=='t4':
        return tab4_layout
    if tabs=='t5':
        return tab5_layout
    if tabs=='t6':
        return tab6_layout



if __name__ == '__main__':
    my_app.run_server()
