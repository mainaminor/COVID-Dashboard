import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import app1, app2, app3, app4

server = app.server

main_color="#181818"
section_header = {'color':"white", 'margin-bottom':'0', 'background-color': "#5c1616", 'padding':"0.5%",'font-size': '3rem','font-weight': 'normal'}


tab_style = {
    'backgroundColor': main_color,
    'border': '1px solid '+main_color,
    'borderBottom': '1px solid'+ main_color,
    'color': 'white',
    #'padding':'2%'   
}

tab_selected_style = {
    'backgroundColor': main_color,
    'border': '1px solid '+ main_color,
    'borderBottom': '2px solid #7CFC00',
    'color': 'white',
    'fontWeight': 'bold',
    #'padding':'2%'
}

app.layout = html.Div([
    html.H5("COVID-19 Information", style = section_header),
    html.Div([
        dcc.Tabs(id='tabs-example', value='tab-1', children=[
            dcc.Tab(label='Worldwide', value='tab-1', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='United States', value='tab-2', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='United Kingdom', value='tab-3', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Country comparison', value='tab-4', style=tab_style, selected_style=tab_selected_style),
            ]),
        html.Div(id='tabs-example-content')
        ],
        style={"padding": "1%", "background-color": main_color},
        id="wrapper"
        ),
    html.Div([#footer
        html.A("Built by Anthony S N Maina", href='https://www.linkedin.com/in/anthonymaina/', target="_blank", style={'font-size': '1rem',"marginBottom": "0%"})
        ],
        className='row',
        style={ 'text-align':'center'}
        ),
    ]
)

@app.callback(Output('tabs-example-content', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return app1.layout
    elif tab == 'tab-2':
        return app3.layout
    elif tab == 'tab-3':
        return app4.layout
    elif tab == 'tab-4':
        return app2.layout

if __name__ == '__main__':
    app.run_server(debug=False)