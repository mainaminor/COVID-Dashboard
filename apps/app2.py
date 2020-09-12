import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np

from app import app

text_color_main="white"
text_color_sub="#D3D3D3"
main_color= "#181818"
background_color = "#181818"
country_border = "#808080"

################################################

url_1='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_2='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
df1=pd.read_csv(url_1)
df2=pd.read_csv(url_2)
df_p=pd.read_csv("data/worldpop.csv").set_index("Location").rename(index={"United States of America": 'United States'})
countries_data=pd.read_csv("data/countries_data.csv").set_index("Unnamed: 0").rename(index={"United States of America": 'United States'})

################################################

def prep_world_data(df):
    df=df.groupby(by="Country/Region").sum()
    df.drop(labels=["Lat", "Long"], axis=1, inplace=True)
    df.loc[:,:str(df.columns[-1])]=np.clip(df.loc[:,:str(df.columns[-1])], a_min=0, a_max=None)
    df.rename(index={"US": 'United States'}, inplace=True)
    return df

world_data_cases= prep_world_data(df1)
world_data_deaths= prep_world_data(df2)

def prep_rolling_avg (scope):
    if scope == "cases":
      d1=world_data_cases
    else:
      d1=world_data_deaths
    sr_7d=pd.DataFrame(index=d1.index,columns=list(d1.columns[7:]))
    for i in range(len(d1.columns)-7):
        f=(d1[d1.columns[i+7]]-d1[d1.columns[i]])/7
        sr_7d[sr_7d.columns[i]]=f
    return sr_7d
    

def prep_world_capita (scope):
    if scope == "cases":
      d1=world_data_cases
    else:
      d1=world_data_deaths
    t=d1.merge(df_p, left_index=True, right_index=True)
    a=t.loc[:, :d1.columns[-1]].values.transpose()
    b=100/t["PopTotal"].values
    c=a*b
    t.loc[:, :d1.columns[-1]]=c.transpose()
    return t

def prep_rolling_capita(scope):
    if scope == "cases":
      d11=world_data_cases
    else:
      d11=world_data_deaths
    d1=prep_world_capita(scope)
    sr_7d=pd.DataFrame(index=d1.index,columns=list(d11.columns[7:]))
    for i in range(len(d11.columns)-7):
        f=(d1[d1.columns[i+7]]-d1[d1.columns[i]])/7
        sr_7d[sr_7d.columns[i]]=f
    return sr_7d

#try:
rolling_avg_cases= prep_rolling_avg("cases")
rolling_avg_deaths= prep_rolling_avg("deaths")
rolling_capita_cases= prep_rolling_capita("cases")
rolling_capita_deaths= prep_rolling_capita("deaths")
world_capita_cases = prep_world_capita("cases")
world_capita_deaths = prep_world_capita("deaths")
'''
  rolling_avg_cases.to_csv("data/rolling_avg_cases.csv")
  rolling_avg_deaths.to_csv("data/rolling_avg_deaths.csv")
  rolling_capita_cases.to_csv("data/rolling_capita_cases.csv")
  rolling_avg_deaths.to_csv("data/rolling_capita_deaths.csv")
'''
#except:
#pass
'''
rolling_capita_cases=pd.read_csv("data/rolling_capita_cases.csv").set_index("Unnamed: 0")
rolling_capita_deaths=pd.read_csv("data/rolling_capita_deaths.csv")#.set_index("Unnamed: 0")
rolling_avg_cases=pd.read_csv("data/rolling_avg_cases.csv").set_index("Country/Region")
rolling_avg_deaths=pd.read_csv("data/rolling_avg_deaths.csv").set_index("Country/Region")
'''

options = []
for tic in rolling_avg_cases.index:
  options.append({'label':tic, 'value':tic})


################################################
#### CHART LAYOUTS #############################
################################################

#HEATMAP & LINE CHART
l_trend=go.Layout(
  height=500,
  margin={"r":10,"t":10,"l":10,"b":10},
  template="plotly_dark",
  paper_bgcolor = main_color,
  plot_bgcolor = main_color,
  yaxis={"tickfont":{"size":10}},
  xaxis={"tickfont":{"size":10}},
  legend={'x':0.01, 'y':0.98, 'font':{'size':10},'itemclick': 'toggleothers'},
  dragmode=False
)



#CHART LAYOUTS

def make_chart_1(selection, trend, uom):
    li=[]
    for c in selection:
        li.append(c)
    if trend == "Cases":
      x=pd.to_datetime(np.array(world_data_cases.columns))
      if uom =="Abs":
          d3=[{
          'x': x,
          'y': world_data_cases[world_data_cases.index==country].values[0],
          'name': country,
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
          return fig3
      else:
          d3=[{
          'x': x,
          'y': world_capita_cases.iloc[:,:-9][world_capita_cases.index==country].values[0],
          'name': country,
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
          return fig3
    else:
      x=pd.to_datetime(np.array(world_data_deaths.columns))
      if uom =="Abs":
          d3=[{
          'x': x,
          'y': world_data_deaths[world_data_deaths.index==country].values[0],
          'name': country,
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
          return fig3
      else:
          d3=[{
          'x': x,
          'y': world_capita_deaths.iloc[:,:-9][world_capita_deaths.index==country].values[0],
          'name': country,
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
          return fig3

def make_chart_2(selection, trend, uom):
    li=[]
    for c in selection:
        li.append(c)
    if trend == "Cases":
      x=pd.to_datetime(np.array(rolling_avg_cases.columns))
      if uom =="Abs":
          d3=[{
          'x': x,
          'y': rolling_avg_cases[rolling_avg_cases.index==country].values[0],
          'name': country,
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
          return fig3
      else:
          d3=[{
          'x': x,
          'y': rolling_capita_cases[rolling_capita_cases.index==country].values[0],
          'name': country,
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
          return fig3
    else:
      x=pd.to_datetime(np.array(rolling_avg_deaths.columns))
      if uom =="Abs":
          d3=[{
          'x': x,
          'y': rolling_avg_deaths[rolling_avg_deaths.index==country].values[0],
          'name': country,
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
          return fig3
      else:
          d3=[{
          'x': x,
          'y': rolling_capita_deaths[rolling_capita_deaths.index==country].values[0],
          'name': country,
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
          return fig3


#HIDE MODEBAR
conf = {'displayModeBar': False}

##########################################
########  STYLES  ########################
##########################################

section_header = {'color':text_color_main, 'font-size': '2rem','background-color': "#181818", "margin-bottom":0}
section_subheader = {'font-size': '1.2rem', 'color': text_color_main,  'background-color': "#181818", 'margin-bottom':0}
main_columns = {'paddingRight':'0%','paddingLeft':'0%'}
section_wrapper = {"padding": "0%"}
section_header2 = {'color':text_color_main, 'margin-bottom':'0','font-size': '1.5rem','padding':"0.5%"}

##########################################
#######  APP LAYOUT ######################
##########################################


layout = html.Div([
  html.Div([#row for header
      html.H5('Comparison by country',
        style={"color":text_color_main, 'margin-bottom':0}
        ),       
      html.P('Data source: Johns Hopkins CSSE',
        style={'font-size': '1rem','color':'#696969', 'color': text_color_sub, 'margin-bottom':0})
      ], 
      className='row subtitle', 
      style={'marginbottom':'15px','paddingTop':'1%','paddingBottom':'1%'},
      ),
  html.Div([#row for body
    html.Div([#six columns for line charts
      html.Div([#row for selector
        html.H6('Select countries for comparison', 
          style={"color":text_color_main, 'margin-bottom':0, 'font-size': '1.65rem','line-height': '1.55','letter-spacing': '-.03rem'},
          ),
        html.Div([
          dcc.RadioItems(
            id="trend",
            options=[
            {'label': 'Cases', 'value': 'Cases'},
            {'label': 'Deaths', 'value': 'Deaths'}
            ],
            value='Cases',
            labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
            ),
          ],
          style=section_subheader
          ),
        html.Div([
          dcc.Dropdown(
            id='country-select',
            options = options,
            value = countries_data.sort_values(by="Confirmed", ascending=False).index[:5],
            multi = True,
            ),
          ],
          style = {'color': text_color_main,  'background-color': main_color, 'margin-bottom':0, 'margin-top':'1%','padding': '0%'}
          )  
        ],
        className="row subtitle",
        ),
      html.Div([#row for charts
        html.Div([#six columns for new cases
          html.Div([#chart headers
            html.H6(id="heatmap-header", children="New Cases (7 day rolling average)",
              style={"color":text_color_main, 'margin-bottom':0}
              ),
            html.Div([#UoM radio items
              dcc.RadioItems(
                id="uom2",
                options=[
                {'label': 'Absolute', 'value': 'Abs'},
                {'label': 'per 100k pop.', 'value': 'per100k'}],
                value='per100k',
                labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
                )
              ],
              style=section_subheader 
              ),
            ],
            className = 'row subtitle',
            style = {'border-left': '5px solid #4039e3'}
            ), 
          html.Div([
            dcc.Loading(
              dcc.Graph(id='heatmap',
              #figure=make_chart_2(countries_data.sort_values(by="Confirmed", ascending=False).index[:5], "Cases", "per100k"),
              config=conf
              )
              )
            ],
            className="row",
            style=section_subheader
            ),
          ], 
          className='six columns',
          style={'margin-bottom': "1%"}
          ),
        html.Div([# six columns for cumulative cases
          html.Div([ #headers
            html.Div([#Chart heading
              html.P(id="line-header",children="Cumulative cases",
                style={"color":text_color_main, 'margin-bottom':0}
                )
              ], 
              ),
            html.Div([#UoM radio items
              dcc.RadioItems(
                id="uom",
                options=[
                {'label': 'Absolute', 'value': 'Abs'},
                {'label': 'per 100k pop.', 'value': 'per100k'}],
                value='per100k',
                labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
                )
              ],
              style=section_subheader 
              ),
            ],
            className="row subtitle",
            style = {'border-left': '5px solid #4039e3'}
            ),
          html.Div([#chart itself
            dcc.Loading(
              dcc.Graph(id="countries-conf",
              #figure=make_chart_1(countries_data.sort_values(by="Confirmed", ascending=False).index[:5], "Cases", "per100k"), 
              config=conf
              ),
              ),
            ],
            className="row",
            style=section_subheader
            ),
          ], 
          className='six columns',
          ),      
        ],
        className='row',
        style = section_wrapper
        ),
      ],
      className="row",
      style={"padding": "0%"}
      )
    ],
    className = "row",
    style = {'background-color': main_color, 'padding':'0'} 
    )
]
)

#Callbacks for Line Chart
@app.callback(
  Output('line-header','children'),
  [Input('trend', 'value')])

def update_header(trend):
  if trend=="Cases":
    return "Cumulative Cases"
  else:
    return "Cumulative Deaths"

@app.callback(
    Output('countries-conf', 'figure'),
    [Input('country-select', 'value'),
    Input('trend', 'value'),
    Input('uom', 'value')])

def update_chart(selection, trend, uom):
    return make_chart_1(selection, trend, uom)

#Callbacks for heatmap
@app.callback(
  Output('heatmap-header','children'),
  [Input('trend', 'value')])

def update_header(trend):
  if trend=="Cases":
    return "New Cases (7 day rolling average)"
  else:
    return "New Deaths (7 day rolling avg)"

@app.callback(
    Output('heatmap', 'figure'),
    [Input('country-select', 'value'),
    Input('trend', 'value'),
    Input('uom2', 'value')])

def update_chart(selection, trend, uom):
  return make_chart_2(selection, trend, uom)