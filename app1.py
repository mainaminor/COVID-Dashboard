import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#external_stylesheets = ['https://codepen.io/mainaminor/pen/wvaOEmY.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, 
  meta_tags=[{"name": "viewport", "content": "width=device-width"}]
  )
server = app.server

################################################
#### DATA FOR WORLDWIDE ANALYSES ###############
################################################

continents=pd.read_csv("data/continents.csv").drop(columns="Unnamed: 0")

df_p=pd.read_csv("data/worldpop.csv").set_index("Location")

countries_data=pd.read_csv("data/countries_data.csv").set_index("Unnamed: 0")
world_data_cases=pd.read_csv("data/world_data_cases.csv").set_index("Country/Region")
world_data_deaths=pd.read_csv("data/world_data_deaths.csv").set_index("Country/Region")
world_trend_cases=pd.read_csv("data/world_trend_cases.csv").set_index("Continent")
world_trend_deaths=pd.read_csv("data/world_trend_deaths.csv").set_index("Continent")
world_newcases_cases=pd.read_csv("data/world_newcases_cases.csv").set_index("Continent")
world_newcases_deaths=pd.read_csv("data/world_newcases_deaths.csv").set_index("Continent")
world_capita_cases=pd.read_csv("data/world_capita_cases.csv").set_index("Unnamed: 0")
world_capita_deaths=pd.read_csv("data/world_capita_deaths.csv").set_index("Unnamed: 0")
rolling_capita_cases=pd.read_csv("data/rolling_capita_cases.csv").set_index("Unnamed: 0")
rolling_capita_deaths=pd.read_csv("data/rolling_capita_deaths.csv").set_index("Unnamed: 0")
rolling_avg_cases=pd.read_csv("data/rolling_avg_cases.csv").set_index("Country/Region")
rolling_avg_deaths=pd.read_csv("data/rolling_avg_deaths.csv").set_index("Country/Region")


world_R=pd.read_csv("data/world_r.csv").set_index("Country/Region")
states_R=pd.read_csv("data/states_r.csv").set_index("Province_State")
uk_R=pd.read_csv("data/uk_r.csv").set_index("ReportingArea")


options = []
for tic in world_data_cases.index:
  options.append({'label':tic, 'value':tic})

li2=list(countries_data[countries_data["PopTotal"]>5000].sample(100, replace=True, random_state=9).index)  



################################################
#### DATA FOR USA ANALYSES #####################
################################################

us_regions=pd.read_csv('data/us_regions.csv').drop("Unnamed: 0", axis=1)
us_pop=pd.read_csv('data/us_pop.csv')

county_data_cases=pd.read_csv("data/county_data_cases.csv").drop(columns="Unnamed: 0")
county_data_deaths=pd.read_csv("data/county_data_deaths.csv").drop(columns="Unnamed: 0")
state_data_cases=pd.read_csv("data/state_data_cases.csv").set_index("Province_State")
state_data_deaths=pd.read_csv("data/state_data_deaths.csv").set_index("Province_State")
county_sum=pd.read_csv("data/county_sum.csv").drop(columns="Unnamed: 0")
state_sum=pd.read_csv("data/state_sum.csv").set_index("STNAME")
us_trend_cases=pd.read_csv("data/us_trend_cases.csv").set_index("Region")
us_trend_deaths=pd.read_csv("data/us_trend_deaths.csv").set_index("Region")
us_newcases_cases=pd.read_csv("data/us_newcases_cases.csv").set_index("Region")
us_newcases_deaths=pd.read_csv("data/us_newcases_deaths.csv").set_index("Region")


################################################
#### DATA FOR UK ANALYSES ######################
################################################


england_cases=pd.read_csv("data/england_cases.csv").drop("Unnamed: 0", axis=1)
wales_cases=pd.read_csv("data/wales_cases.csv").drop("Unnamed: 0", axis=1)
scot_cases=pd.read_csv("data/scot_cases.csv").drop("Unnamed: 0", axis=1)
eng_trend=pd.read_csv("data/eng_trend.csv").drop("Unnamed: 0", axis=1)
wales_trend=pd.read_csv("data/wales_trend.csv").drop("Unnamed: 0", axis=1)
scot_trend=pd.read_csv("data/scot_trend.csv").drop("Unnamed: 0", axis=1)
uk_map=pd.read_csv("data/uk_map.csv").drop(columns="Unnamed: 0").groupby(by="ReportingArea").mean()
uk_pop=pd.read_csv("data/uk_pop.csv").drop(columns="Unnamed: 0").groupby(by="ReportingArea").sum()
uk_scatter=pd.read_csv("data/uk_scatter.csv").set_index("ReportingArea")
ewss=pd.read_csv("data/ews.csv").drop(columns="Unnamed: 0")
ews=ewss.drop(columns="Specimen date")
ews["Specimen date"]=pd.to_datetime(ewss["Specimen date"])

e=pd.to_datetime(eng_trend["Specimen date"])
w=pd.to_datetime(wales_trend["Specimen date"])
s=pd.to_datetime(scot_trend["Specimen date"])

max_date=min(max(e), max(w), max(s))
min_date=max(min(e), min(w), min(s))


################################################
#### CHART LAYOUTS #############################
################################################

#WORLD & US MAPS
l_map=go.Layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    geo={
    'visible': True, 
    'resolution':50, 
    'showcountries':True, 
    'countrycolor':"grey",
    'showsubunits':True, 
    'subunitcolor':"White",
    'showframe':False,
    'coastlinecolor':"slategrey",
    'countrycolor':'white',
    }
)

#UK Map
l_mapbox=go.Layout(
  margin={"r":0,"t":0,"l":0,"b":0},
  mapbox_style="carto-positron",
  mapbox={
    'bearing':0,
    'center':go.layout.mapbox.Center(lat=55.7781,lon=-3.6360),
    'pitch':0,
    'zoom':4
    },
  
 )

#HEATMAP & LINE CHART
l_trend=go.Layout(
  margin={"r":0,"t":30,"l":0,"b":0},
  template="plotly_white",
  yaxis={"tickfont":{"size":10}},
  xaxis={"tickfont":{"size":10}},
  legend={'x':0.01, 'y':0.98, 'font':{'size':10}},
  dragmode=False
)

#WORLD BARS
l_bar_w=go.Layout(
  height=250,
  #width=90,
  margin={"r":5,"t":0,"l":0,"b":0},
  template="plotly_white",
  yaxis={"tickfont":{"size":9}},
  xaxis={"tickfont":{"size":9}},
  legend={'x':0.02, 'y':0.96, 'font':{'size':9}, 'itemclick': 'toggleothers'},
  dragmode=False
  )

#SIMPLE BARS
l_bar_s=go.Layout(
  height=175,
  margin={"r":0,"t":0,"l":0,"b":0},
  template="plotly_white",
  yaxis={"tickfont":{"size":9}},
  xaxis={"tickfont":{"size":9}},
  legend={'x':0.02, 'y':0.96, 'font':{'size':9}, 'itemclick': 'toggleothers'},
  dragmode=False
  )

#SIMPLE BUBBLE
l_bub_s=go.Layout(
  height=400,
  margin={"r":0,"l":0,"t":0},
  template="ggplot2",
  yaxis={"tickfont":{"size":9}},
  xaxis={"tickfont":{"size":9}},
  #legend={'x':0.02, 'y':0.96, 'font':{'size':9}, 'itemclick': 'toggleothers'},
  dragmode=False,
  font=dict(
        size=10,
        #color="#7f7f7f"
    )
  )


#HIDE MODEBAR
conf = {'displayModeBar': False}


################################################
################ CHARTS ########################
################################################


#Reporting Area total cases

def make_fig_2_3(d1,d2,text):
  fig = go.Figure(go.Bar(y=countries_data.sort_values(by=[text], ascending=True).index[-15:],
                          x=countries_data.sort_values(by=[text],ascending=True)[text][-15:],
                         orientation='h'
                        )
                 )
  fig.update_layout(l_bar_s)
  return fig

#Cumulative cases by continent

def make_fig_4(d):
  fig = go.Figure(data=[go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[0],
                          name=d.index[0]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[1],
                          name=d.index[1]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[2],
                          name=d.index[2]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[3],
                          name=d.index[3]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[4],
                          name=d.index[4]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[5],
                          name=d.index[5])]
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig


#Trend new cases by continent
def make_fig_5(d):
  fig = go.Figure(data=[go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[0],
                          name=d.index[0]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[1],
                          name=d.index[1]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[2],
                          name=d.index[2]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[3],
                          name=d.index[3]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[4],
                          name=d.index[4]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[5],
                          name=d.index[5]),
                        ]
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig

#County total cases
def make_fig_7_8(d, text):
  fig = go.Figure(go.Bar(y=d.sort_values(by=[text], ascending=True).index[-15:],
                          x=d.sort_values(by=[text],ascending=True)[text][-15:],
                         orientation='h'
                        )
                 )
  fig.update_layout(l_bar_s)
  return fig

#Region cululative cases

def make_fig_9(d):
  fig = go.Figure(data=[go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[0],
                          name=d.index[0]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[1],
                          name=d.index[1]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[2],
                          name=d.index[2]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[3],
                          name=d.index[3])]
                                
                         #orientation='h'
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig

#New cases by region

def make_fig_10(d):
  fig = go.Figure(data=[go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[0],
                          name=d.index[0]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[1],
                          name=d.index[1]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[2],
                          name=d.index[2]),
                        go.Bar(x=pd.to_datetime(np.array(d.columns)),
                          y=d.iloc[3],
                          name=d.index[3])]
                         #orientation='h'
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig


#Worst hit regions
def make_fig_12_13(text):
  fig = go.Figure(go.Bar(y=ews[ews["Specimen date"]==max_date].sort_values(by=text, ascending=True)["ReportingArea"],
                          x=ews[ews["Specimen date"]==max_date].sort_values(by=text,ascending=True)[text],
                         orientation='h'
                        )
                 )
  fig.update_layout(l_bar_s)
  return fig

def make_fig_14(d1,d2,d3):
  fig = go.Figure(data=[go.Bar(x=d1[d1["ReportingArea"]=="England"]["Specimen date"],
                          y=d1[d1["ReportingArea"]=="England"]["Cumulative cases"],
                          name="England"),
                        go.Bar(x=d2.groupby("Specimen date").sum().index,
                          y=d2.groupby("Specimen date").sum()["Cumulative cases"],
                          name="Wales"),
                        go.Bar(x=d3["Specimen date"],
                          y=d3["Cumulative cases"],
                          name="Scotland")]
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig

def make_fig_15(d1,d2,d3):
  fig = go.Figure(data=[go.Bar(x=d1[d1["ReportingArea"]=="England"]["Specimen date"],
                          y=d1[d1["ReportingArea"]=="England"]["New cases"],
                          name="England"),
                        go.Bar(x=d2.groupby("Specimen date").sum().index,
                          y=d2.groupby("Specimen date").sum()["New cases"],
                          name="Wales"),
                        go.Bar(x=d3["Specimen date"][1:],
                          y=d3["Cumulative cases"][1:].values - d3["Cumulative cases"][:-1].values,
                          name="Scotland")]
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig

#RCHART
def make_R_chart(k, size):
    fig = go.Figure(go.Bar(y=k.iloc[:,-1].sort_values(ascending=True).index[-15:],
                              x=k.iloc[:,-1].sort_values(ascending=True)[-15:],
                             orientation='h',
                           marker_color='salmon'
                            )
                     )
    if size=="big":
      fig.update_layout(l_bar_w)
    else:
      fig.update_layout(l_bar_s)
    return fig



################################################
#### APP LAYOUT  ###############################
################################################

app.layout = html.Div([

  #BLOCK FOR WORLD
  html.Div([#row for world headers
    html.H5('Worldwide as of {}'.format(pd.to_datetime(world_data_cases.columns[-1]).strftime('%B %d, %Y'))),       
    html.P('Data source: Johns Hopkins CSSE. Note: The CSSE states that its numbers rely upon publicly available data from multiple sources, which do not always agree',style={'font-size': '1rem','color':'#696969'})
    ], 
    className='row flex-display', 
    style={'marginbottom':'15px','padding':'1%'},
    ),
  html.Div([#row for world body
    html.Div([#seven columns for LHS
      html.Div([#row for tiles
        html.Div([#four columns for cases
          html.P('Cases:', 
            style={'color':'#696969', 'font-size': '1rem'}
            ),
          html.P('{}'.format(f'{world_data_cases[str(world_data_cases.columns[-1])].sum():,}'), 
            style={'font-size': '1.5rem'}
            )
          ],
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        html.Div([#four columns for deaths
          html.P('Deaths:', 
            style={'color':'#696969','font-size': '1rem'}
            ),
          html.P('{}'.format(f'{world_data_deaths[str(world_data_deaths.columns[-1])].sum():,}'), 
            style={'font-size': '1.5rem'}
            )
          ],
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        html.Div([#four columns for mortality
          html.P('Avg mortality:', 
            style={'color':'#696969','font-size': '1rem'}
            ),
          html.P('{} % '.format(round(100*world_data_deaths[str(world_data_deaths.columns[-1])].sum()/world_data_cases[str(world_data_cases.columns[-1])].sum(),2)), 
            style={'font-size': '1.5rem'}
            )
          ], 
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%','border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        ], 
        className='row flex-display', 
        ),
      html.Div([#row for world map
        html.Div([#row for world map header
          html.Div([#eight columns for world header text
            html.H6('Spread by location',style = {'margin-bottom':'0', 'paddingBottom':'0','font-size': '1.5rem'}),
            html.P('Click for detail',style={'color':'#696969','font-size': '1rem', 'font-style':'italic'})
            ],
            className='eight columns'
            ),
          html.Div([#four columns for world header radio buttons
            dcc.RadioItems(
              id="uom-ww-map",
              options=[
              {'label': 'Absolute', 'value': 'Abs'},
              {'label': 'per 100k pop.', 'value': 'per100k'}],
              value='Abs',
              labelStyle={'display': 'inline-block'},
              style={'font-size': '1rem', 'float':'right'},
            ),
            ],
            className='four columns'
            ),
          ], 
          className='row'
          ),
        html.Div([#row for world map chart
          dcc.Graph(id= "world", config=conf)
          ],
          className='row',
          style={'padding':'1.5%'}
          ),
        ],
        className='row',
        style={'padding':'1%'}
        ),
      ],
      className='six columns',
      style={'padding':'1%'},
      ),
    html.Div([#five columns for RHS
      html.Div([#row for cumulative cases
        html.Div([# row for cumulative cases headers
          html.Div([#eight columns for header text
            html.P(id='world-cum-title',style={'margin':0,'font-size': '1.2rem'}),
            html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
            ], 
            className="eight columns"
            ),
          html.Div([#four columns for radio buttons
            dcc.RadioItems(
            id="world-cum",
            options=[
            {'label':  'Cases', 'value': 'Cases'},
            {'label': 'Deaths', 'value': 'Deaths'}],
            value='Cases',
            labelStyle={'display': 'inline-block'},
            style={'font-size': '1rem', 'float':'right'},
            )
            ],
            className="four columns"
            )
          ],
          className='row'
          ),
        html.Div([#row for cumulative cases graph
          dcc.Graph(id='world-trend-cum',config=conf),
          ],
          className='row',
          style={'marginbottom':'20%','paddingBottom': '5%'},
          ),
        ],
        className='row',
        style={'paddingTop':'2.5%', 'paddingBottom':'2.5%'}
        ),
      html.Div([# row for new cases
        html.Div([#row for new cases headers
          html.Div([#eight columns for header text
            html.P(id='world-new-title', style={'margin':0,'font-size': '1.2rem'}),
            html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
            ], 
            className="eight columns"
            ),
          html.Div([#four columns for radio buttons
            dcc.RadioItems(
              id="world-new",
              options=[
              {'label':  'Cases', 'value': 'Cases'},
              {'label': 'Deaths', 'value': 'Deaths'}],
              value='Cases',
              labelStyle={'display': 'inline-block'},
              style={'font-size': '1rem','float':'right'},
            )
            ],
            className="four columns"
            )
          ],
          className='row'
          ),
        html.Div([#row for new cases graph
          dcc.Graph(id='world-trend-new', config=conf),
          ],
          className='row',
          ),  
        ],
        className='row',
        style={'paddingTop':'2.5%', 'paddingBottom':'2.5%'}
        ),
      html.Div([#row for charts and headers
        html.Div([#eight columns for worst hit
          html.Div([#row for headers
            html.Div([# row for text and radio buttons separation
              html.Div([# eight columns for title text
                html.P("Worst hit countries (as of {})".format(world_data_cases.columns[-1]), style={'font-size': '1.2rem'}),
                ],
                className='eight columns'
                ),
              html.Div([# four columns for radio buttons
                dcc.RadioItems(
                  id="top-countries",
                  options=[
                  {'label':  'Cases', 'value': 'Cases'},
                  {'label': 'Deaths', 'value': 'Deaths'}],
                  value='Cases',
                  labelStyle={'display': 'inline-block'},
                  style={'font-size': '1rem','float':'right'},
                )
                ],
                className="four columns"
                ),
              ],
              className='row'
              ),
            ],
            className='row'
            ),
          html.Div([#row for charts
            html.Div([ # row for charts themselves
              html.Div([ # six columns for total
                html.Div([
                  html.P('Total',
                    style={'font-size': '1rem'}),
                  dcc.Graph(id='country-total',config=conf,style={'margin':'2%'})
                  ],
                  ),
                ],
                className='six columns'
                ),
              html.Div([#six columns for per100k
                html.Div([
                  html.P('per 100k pop.',
                    style={'font-size': '1rem'}),
                  dcc.Graph(id='country-capita',config=conf,)
                  ],
                  ),
                ],
                className='six columns'
                ),
              ],
              className='row'
              ),
            ],
            className='row'
            ),
          ],
          className='eight columns',
          style={'padding':'1%','margin-bottom':'5%'}
          ),
        html.Div([#four columns for R calculation
          html.Div([#chart title
            html.P("Highest transmission rates",style={'font-size': '1.2rem'})
            ],
            className='row',
            style={'paddingTop':'2%', 'paddingBottom':'2%'}
            ),
          html.Div([#chart itself
            html.P("Estimated R number*",style={'font-size': '1rem'}),
            dcc.Graph(figure=make_R_chart(world_R, "small"), config=conf)
            ],
            className='row'
            ),
          ],
          className='four columns',
          style={'padding':'1%','margin-bottom':'5%'}
          ),
        ],
        className='row',
        style={'paddingTop':'2.5%', 'paddingBottom':'2.5%'}
        ),
      html.Div([#footnote
        html.P('*number of people each new victim infects',
          style={'font-size': '1rem','color':'#696969'}),
        ],
        className='row',
        style={"paddingLeft":'2%'}
        ),
      ],
      className='six columns',
      style={'paddingRight':'1%','paddingLeft':'1%'},
      ),
    ],
    className='row'
    ),
  

  ##BLOCK FOR HEATMAP AND COUNTRY TREND
  html.Div([#row for header
    html.Div([
      html.H6('Select countries for comparison', 
        style={'font-size': '1.5rem'}
        ),
      dcc.Dropdown(
        id='country-select',
        options = options,
        value = countries_data.sort_values(by="Confirmed", ascending=False).index[:5],
        multi = True)
      ], 
      className="eight columns", 
      style={'font-size': '1rem'}
      ),
    html.Div([
      html.H6('Select trend', 
        style={'font-size': '1.5rem'}
        ),
      dcc.RadioItems(
        id="trend",
        options=[
        {'label': 'Cases', 'value': 'Cases'},
        {'label': 'Deaths', 'value': 'Deaths'}],
        value='Cases')
      ], 
      className='two columns', 
      style={'font-size': '1rem','float':'right'}
      ),
    ], 
    className='row flex-display', 
    style={'padding':'1%', 'background-color':'#F5F5F5', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'1%'}
    ),
  html.Div([#row for body
    html.Div([#six columns for line chart
      html.H6(id="line-header",style = {'margin':0,'font-size':'1.5rem'}),
      #html.P('Click on legend item to hide line', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
      dcc.RadioItems(
        id="uom",
        options=[
        {'label': 'Absolute', 'value': 'Abs'},
        {'label': 'per 100k pop.', 'value': 'per100k'}],
        value='per100k',
        labelStyle={'display': 'inline-block'},
        style={'font-size': '1rem'}),
      dcc.Graph(id="countries-conf",config=conf,style={'margin':'0%','padding': '2%'}),
      ], 
      className='six columns',
      style={'padding':'2%'}
      ),
    html.Div([#six columns for heatmap
      html.H6(id="heatmap-header", style = {'font-size':'1.5rem'}),
      #html.H6("new cases per 100k pop per day (7d rolling average)", style = {'font-size':'1rem'}),
      dcc.RadioItems(
        id="uom2",
        options=[
        {'label': 'Absolute', 'value': 'Abs'},
        {'label': 'per 100k pop.', 'value': 'per100k'}],
        value='per100k',
        labelStyle={'display': 'inline-block'},
        style={'font-size': '1rem'}),
      dcc.Graph(id='heatmap',config=conf, style={'margin':'0%','padding': '2%'})
      ], 
      className='six columns',style={'padding':'2%'}
      ),
    ],
    className='row flex-display',
    style={'padding':'1%'},
    ),
  
  #BLOCK FOR US
  html.Div([#row for US header
    html.H5('USA as of {}'.format(pd.to_datetime(world_data_cases.columns[-1]).strftime('%B %d, %Y'))),       
    html.P('Data source: Johns Hopkins CSSE. Note: The CSSE states that its numbers rely upon publicly available data from multiple sources, which do not always agree',style={'font-size': '1rem','color':'#696969'})
    ], 
    className='row', 
    style={'marginbottom':'15px','padding':'1%'},
    ),
  html.Div([#row for US body
    html.Div([#seven columns for LHS
      html.Div([#row for tiles
        html.Div([#cases
          html.P('Cases:',style={'color':'#696969', 'font-size': '1rem'}),
          html.P('{}'.format(f'{world_data_cases[world_data_cases.columns[-1]]["United States of America"]:,}'), 
            style={'font-size': '1.5rem'}
            )
          ],
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        html.Div([#deaths
          html.P('Deaths:',style={'color':'#696969','font-size': '1rem'}),
          html.P('{}'.format(f'{world_data_deaths[world_data_deaths.columns[-1]]["United States of America"]:,}'),style={'font-size': '1.5rem'})
          ],
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        html.Div([#mortality
          html.P('Avg mortality:', style={'color':'#696969','font-size': '1rem'}),
          html.P('{} % '.format(round(100*world_data_deaths[world_data_deaths.columns[-1]]["United States of America"]/world_data_cases[world_data_cases.columns[-1]]["United States of America"],2)), style={'font-size': '1.5rem'})
          ],
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%','border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        ],
        className='row', 
        ),
      html.Div([#row for US map
        html.Div([# row for US map titles
          html.Div([#title text
            html.H6('Spread by location',style = {'margin-bottom':'0', 'paddingBottom':'0','font-size': '1.5rem'}),
            html.P('Click for detail',style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
            ],
            className='eight columns'),
          html.Div([#radio items
            dcc.RadioItems(
              id="uom-us-map",
              options=[
              {'label': 'Absolute', 'value': 'Abs'},
              {'label': 'per 100k pop.', 'value': 'per100k'}],
              value='Abs',
              labelStyle={'display': 'inline-block'},
              style={'font-size': '1rem','float':'right'}
              ),
            ], 
            className='four columns'
            )
          ], 
          className='row'
          ),
        html.Div([#row for US map itself
          dcc.Graph(id= "US map",config=conf)
          ],
          className='row',
          ),
        ],
        className='row',
        style={'padding':'1%'}
        ),
      ],
      className='six columns',
      style={'padding':'1%'},
      ),
    html.Div([#five columns for RHS
      html.Div([#row for cum cases
        html.Div([#row for titles
          html.Div([#eight columns for text
            html.P(id='us-cum-title',style={'margin':0,'font-size': '1.2rem'}),
            html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
            ], 
            className="eight columns"
            ),
          html.Div([#four columns for radio items
            dcc.RadioItems(
              id="us-cum",
              options=[
              {'label':  'Cases', 'value': 'Cases'},
              {'label': 'Deaths', 'value': 'Deaths'}],
              value='Cases',
              labelStyle={'display': 'inline-block'},
              style={'font-size': '1rem','float':'right'},
            )
            ],
            className="four columns"
            )
          ],
          className='row'
          ),
        html.Div([#row for chart itself
          dcc.Graph(id='us-trend-total', config=conf),
          ],
          className='row'
          ),
        ],
        className='row',
        style={'margin-top':'5%', 'margin-bottom':'5%'}
        ),
      html.Div([#row for new cases
        html.Div([#row for titles
          html.Div([#eight columns for text
            html.P(id='us-new-title',style={'margin':0,'font-size': '1.2rem'}),
            html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
            ], 
            className="eight columns"
            ),
          html.Div([#four columns for radio items
            dcc.RadioItems(
              id="us-new",
              options=[
              {'label':  'Cases', 'value': 'Cases'},
              {'label': 'Deaths', 'value': 'Deaths'}],
              value='Cases',
              labelStyle={'display': 'inline-block'},
              style={'font-size': '1rem','float':'right'},
            )
            ],
            className="four columns"
            )
          ],
          className='row'),
        html.Div([#row for chart itself
          dcc.Graph(id='us-trend-new', config=conf),
          ],
          className='row'
          ),
        ],
        className='row',
        style={'margin-top':'5%', 'margin-bottom':'5%'}
        ),
      html.Div([#row for bar charts
        html.Div([#eight columns for worst hit
          html.Div([#row for titles
              html.Div([#eight columns for text
                html.P("Worst hit states",style={'font-size': '1.2rem'}),
                ], 
                className='eight columns'),
              html.Div([#four columns for radio buttons
                dcc.RadioItems(
                  id="top-states",
                  options=[
                  {'label':  'Cases', 'value': 'Cases'},
                  {'label': 'Deaths', 'value': 'Deaths'}],
                  value='Cases',
                  labelStyle={'display': 'inline-block'},
                  style={'font-size': '1rem','float':'right'},
                ),
                ],
                className="four columns"
                ),
              ],
              className='row'
              ),
          html.Div([#row for charts
            html.Div([#six columns for total
                html.P('Total',
                  style={'font-size': '1rem'}),
                dcc.Graph(id='us-total',config=conf),
                ], 
                className="six columns"
                ),
            html.Div([#six columns for per 100k
                html.P('per 100k pop.',
                  style={'font-size': '1rem'}),
                dcc.Graph(id='us-capita',config=conf)
                ],
                className='six columns'
                ),      
              ],
              className='row'
              ),
          ],
          className='eight columns',
          style={'padding':'1%','margin-bottom':'5%'}
          ),
        html.Div([#four columns for R calculation
          html.Div([#chart title
            html.P("Highest transmission rates",style={'font-size': '1.2rem'})
            ],
            className='row'
            ),
          html.Div([#chart itself
            html.P("Estimated R number*",style={'font-size': '1rem'}),
            dcc.Graph(figure=make_R_chart(states_R, "small"), config=conf)
            ],
            className='row'
            ),
          ],
          className='four columns',
          style={'padding':'1%','margin-bottom':'5%'}
          ),
        ],
        className='row',
        ),
      html.Div([#footnote
        html.P('*number of people each new victim infects',
          style={'font-size': '1rem','color':'#696969'}),
        ],
        className='row',
        style={"paddingLeft":'2%'}
        ),
      ],
      className='six columns',
      style={'paddingRight':'1%','paddingLeft':'1%'},
      ),
    ],
    className='row'
    ),
    
  #BLOCK FOR UK
  html.Div([#row for UK header
    html.H5('United Kingdom as of {}'.format(pd.to_datetime(world_data_cases.columns[-1]).strftime('%B %d, %Y'))),       
    html.P('Data source: Public Health England, Public Health Wales, Scottish Government. Local and national sub-totals are NHS only, and do not include results from testing by commercial partners.',style={'font-size': '1rem','color':'#696969'})
    ], 
    className='row', 
    style={'marginbottom':'15px','padding':'1%'},
    ),
  html.Div([#row for UK body
    html.Div([#LHS seven columns
      html.Div([#row for title tiles
        html.Div([#cases
          html.P('Cases:', 
            style={'color':'#696969', 'font-size': '1rem'}
            ),
          html.P('{}'.format(f'{world_data_cases[world_data_cases.columns[-1]]["United Kingdom"]:,}'), 
            style={'font-size': '1.5rem'}
            )
          ],
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        html.Div([#deaths
        html.P('Deaths:', 
          style={'color':'#696969','font-size': '1rem'}
          ),
        html.P('{}'.format(f'{world_data_deaths[world_data_deaths.columns[-1]]["United Kingdom"]:,}'), 
          style={'font-size': '1.5rem'}
          )
        ],
        className='four columns',
        style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
        ),
        html.Div([#mortality
        html.P('Avg mortality:', 
          style={'color':'#696969','font-size': '1rem'}
          ),
        html.P('{} % '.format(round(100*world_data_deaths[world_data_deaths.columns[-1]]["United Kingdom"]/world_data_cases[world_data_cases.columns[-1]]["United Kingdom"],2)), 
          style={'font-size': '1.5rem'}
          )
        ], 
        className='four columns',
        style={'background-color':'#F5F5F5','padding':'1%','border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
        ),
        ],
        className='row',
        ),
      html.Div([#row for map
      html.Div([# row for map titles
        html.Div([#title text eight columns
          html.H6('Spread by location (excl. Northern Ireland)',
            style = {'margin-bottom':'0', 'paddingBottom':'0','font-size': '1.5rem'}),
          html.P('Click for detail',
            style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
          ],
          className='eight columns'
          ),
        html.Div([#radio items four columns
          dcc.RadioItems(
            id="uom-uk-map",
            options=[
            {'label': 'Absolute', 'value': 'Abs'},
            {'label': 'per 100k pop.', 'value': 'per100k'}],
            value='Abs',
            labelStyle={'display': 'inline-block'},
            style={'font-size': '1rem','float':'right'}
            ),
          ], 
          className='four columns'
          ),
        ], 
        className='row',
        ),
      html.Div([# row for map itself
        dcc.Graph(id= "UK map",config=conf,)
        ],
        className='row',
        style={'padding':'1%'}
        ),
      ],
      className='row',
      style={'padding':'1%'}
      ),
      ],
      className='six columns',
      style={'padding':'1%'},
      ),
    html.Div([#five columns for RHS
      html.Div([#row for cumulative cases
        html.Div([#row for titles
        html.Div([#eight columns for title text
          html.P(id='uk-cum-title',
            style={'margin':0,'font-size': '1.2rem'}),
          html.P('Click on legend item to zoom in', 
            style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
          ],
          className='eight columns'),
        html.Div([#four columns for radio buttons
          dcc.RadioItems(
              id="uk-cum",
              options=[
              {'label':  'Cases', 'value': 'Cases'},
              {'label': 'Deaths', 'value': 'Deaths'}],
              value='Cases',
              labelStyle={'display': 'inline-block'},
              style={'font-size': '1rem','float':'right'},
            )
          ],
          className='four columns'
          ),
        ],
        className='row'
        ),
        html.Div([#row for dcc cum chart
        dcc.Graph(id='uk-trend-total',config=conf, 
        )
        ],
        className='row'
        ),
        ], 
        className='row',
        style={'margin-bottom':'4%'}
        ),
      html.Div([#row for new cases
        html.Div([#row for titles
          html.Div([#eight columns for title text
            html.P(id='uk-new-title',
                style={'margin':0,'font-size': '1.2rem'}),
            html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
            ], 
            className="eight columns"
            ),
          html.Div([#four columns for title radio buttons
            dcc.RadioItems(
              id="uk-new",
              options=[
              {'label':  'Cases', 'value': 'Cases'},
              {'label': 'Deaths', 'value': 'Deaths'}],
              value='Cases',
              labelStyle={'display': 'inline-block'},
              style={'font-size': '1rem','float':'right'},
            )
            ],
            className="four columns"
            ),
          ],
          className='row'
          ),
        html.Div([#row for new cases dcc chart
          dcc.Graph(id='uk-trend-new',config=conf)
          ],
          className='row',
          style={'margin-top':'5%', 'margin-bottom':'5%'}
          ),
        ],
        className='row'
        ),
      html.Div([#row for bar charts
        html.Div([#eight columns for worst hit
          html.Div([#row for titles
              html.Div([#eight columns for text
                html.P("Regions",style={'font-size': '1.2rem'}),
                ], 
                className='eight columns'),
              ],
              className='row'
              ),
          html.Div([#row for charts
            html.Div([#six columns for total
                html.P('Total',
                  style={'font-size': '1rem'}),
                dcc.Graph(figure=make_fig_12_13("Cumulative cases"),config=conf),
                ], 
                className="six columns"
                ),
            html.Div([#six columns for per 100k
                html.P('per 100k pop.',
                  style={'font-size': '1rem'}),
                dcc.Graph(figure=make_fig_12_13("Conf100"),config=conf)
                ],
                className='six columns'
                ),      
              ],
              className='row'
              ),
          ],
          className='eight columns',
          style={'padding':'1%','margin-bottom':'5%'}
          ),
        html.Div([#four columns for R calculation
          html.Div([#chart title
            html.P("Transmission rate",style={'font-size': '1.2rem'})
            ],
            className='row'
            ),
          html.Div([#chart itself
            html.P("Estimated R number*",style={'font-size': '1rem'}),
            dcc.Graph(figure=make_R_chart(uk_R, "small"), config=conf)
            ],
            className='row'
            ),
          ],
          className='four columns',
          style={'padding':'1%','margin-bottom':'5%'}
          ),
        ],
        className='row',
        ),
      html.Div([#footnote
        html.P('*number of people each new victim infects',
          style={'font-size': '1rem','color':'#696969'}),
        ],
        className='row',
        style={"paddingLeft":'2%'}
        ),
      ],
      className='six columns',
      style={'paddingLeft': '1%','paddingRight':'0.5%'}
      ),
    ],
    className='row'
    ),

],
)


################################################
#### APP CALLBACKS  ############################
################################################


#Callback for world map UoM
@app.callback(
  Output('world', 'figure'),
  [Input('uom-ww-map', 'value')])
def update_chart(units):
  if units == 'per100k':
    s= 0.5*countries_data["Conf100"]
    t=countries_data['text100']
  else:
    s=0.003*countries_data["Confirmed"]
    t=countries_data['text']
  d = go.Figure(go.Scattergeo(
    lon=countries_data["longitude"],
    lat=countries_data["latitude"],
    text = t,
    hoverinfo = 'text',
    marker=dict(
        size= s,
        line_width=0.5,
        sizemode='area'
    )))
  fig1=go.Figure(data=d)
  fig1.update_layout(l_map)
  fig1.update_geos(projection_type="natural earth", lataxis_showgrid=False, lonaxis_showgrid=False)
  return fig1

#Callbacks for RHS World charts

@app.callback(
  Output('world-trend-cum', 'figure'),
  [Input('world-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_4(world_trend_cases)
  else:
    return make_fig_4(world_trend_deaths)

@app.callback(
  Output('world-cum-title', 'children'),
  [Input('world-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "Cumulative cases"
  else:
    return "Cumulative deaths"

@app.callback(
  Output('world-trend-new', 'figure'),
  [Input('world-new', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_5(world_newcases_cases)
  else:
    return make_fig_5(world_newcases_deaths)

@app.callback(
  Output('world-new-title', 'children'),
  [Input('world-new', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "New cases"
  else:
    return "New deaths"

#Callbacks for top15 countries
@app.callback(
  Output('country-total', 'figure'),
  [Input('top-countries', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_2_3(world_data_cases,world_data_deaths,"Confirmed")
  else:
    return make_fig_2_3(world_data_cases,world_data_deaths,"Deaths")

@app.callback(
  Output('country-capita', 'figure'),
  [Input('top-countries', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_2_3(world_data_cases,world_data_deaths,"Conf100")
  else:
    return make_fig_2_3(world_data_cases,world_data_deaths,"Deaths100")

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
          'line': {'color':'#D3D3D3', 'width': 1},
          'showlegend': False
          } for country in li2]
          fig3=go.Figure(data=d3,layout=l_trend)
          for i in li:
            fig3.add_trace(go.Scatter({
                'x': x,
                'y':world_data_cases[world_data_cases.index==i].values[0],
                'name': i}
                )
            )
          return fig3
      else:
          d3=[{
          'x': x,
          'y': world_capita_cases.iloc[:,:-9][world_capita_cases.index==country].values[0],
          'name': country,
          'line': {'color':'#D3D3D3', 'width': 1},
          'showlegend': False
          } for country in li2]
          fig3=go.Figure(data=d3,layout=l_trend)
          for i in li:
            fig3.add_trace(go.Scatter({
                'x': x,
                'y':world_capita_cases.iloc[:,:-9][world_capita_cases.index==i].values[0],
                'name': i}
                )
            )
          return fig3
    else:
      x=pd.to_datetime(np.array(world_data_deaths.columns))
      if uom =="Abs":
          d3=[{
          'x': x,
          'y': world_data_deaths[world_data_deaths.index==country].values[0],
          'name': country,
          'line': {'color':'#D3D3D3', 'width': 1},
          'showlegend': False
          } for country in li2]
          fig3=go.Figure(data=d3,layout=l_trend)
          for i in li:
            fig3.add_trace(go.Scatter({
                'x': x,
                'y':world_data_deaths[world_data_deaths.index==i].values[0],
                'name': i}
                )
            )
          return fig3
      else:
          d3=[{
          'x': x,
          'y': world_capita_deaths.iloc[:,:-9][world_capita_deaths.index==country].values[0],
          'name': country,
          'line': {'color':'#D3D3D3', 'width': 1},
          'showlegend': False
          } for country in li2]
          fig3=go.Figure(data=d3,layout=l_trend)
          for i in li:
            fig3.add_trace(go.Scatter({
                'x': x,
                'y':world_capita_deaths.iloc[:,:-9][world_capita_deaths.index==i].values[0],
                'name': i}
                )
            )
          return fig3

#Callbacks for heatmap
@app.callback(
  Output('heatmap-header','children'),
  [Input('trend', 'value')])

def update_header(trend):
  if trend=="Cases":
    return "New Cases (7d rolling avg)"
  else:
    return "New Deaths (7d rolling avg)"

@app.callback(
    Output('heatmap', 'figure'),
    [Input('country-select', 'value'),
    Input('trend', 'value'),
    Input('uom2', 'value')])

def update_chart(selection, trend, uom):
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
          'line': {'color':'#D3D3D3', 'width': 1},
          'showlegend': False
          } for country in li2]
          fig3=go.Figure(data=d3,layout=l_trend)
          for i in li:
            fig3.add_trace(go.Scatter({
                'x': x,
                'y':rolling_avg_cases[rolling_avg_cases.index==i].values[0],
                'name': i}
                )
            )
          return fig3
      else:
          d3=[{
          'x': x,
          'y': rolling_capita_cases[rolling_capita_cases.index==country].values[0],
          'name': country,
          'line': {'color':'#D3D3D3', 'width': 1},
          'showlegend': False
          } for country in li2]
          fig3=go.Figure(data=d3,layout=l_trend)
          for i in li:
            fig3.add_trace(go.Scatter({
                'x': x,
                'y':rolling_capita_cases[rolling_capita_cases.index==i].values[0],
                'name': i}
                )
            )
          return fig3
    else:
      x=pd.to_datetime(np.array(rolling_avg_deaths.columns))
      if uom =="Abs":
          d3=[{
          'x': x,
          'y': rolling_avg_deaths[rolling_avg_deaths.index==country].values[0],
          'name': country,
          'line': {'color':'#D3D3D3', 'width': 1},
          'showlegend': False
          } for country in li2]
          fig3=go.Figure(data=d3,layout=l_trend)
          for i in li:
            fig3.add_trace(go.Scatter({
                'x': x,
                'y':rolling_avg_deaths[rolling_avg_deaths.index==i].values[0],
                'name': i}
                )
            )
          return fig3
      else:
          d3=[{
          'x': x,
          'y': rolling_capita_deaths[rolling_capita_deaths.index==country].values[0],
          'name': country,
          'line': {'color':'#D3D3D3', 'width': 1},
          'showlegend': False
          } for country in li2]
          fig3=go.Figure(data=d3,layout=l_trend)
          for i in li:
            fig3.add_trace(go.Scatter({
                'x': x,
                'y':rolling_capita_deaths[rolling_capita_deaths.index==i].values[0],
                'name': i}
                )
            )
          return fig3


#Callback for US map UoM
@app.callback(
  Output('US map', 'figure'),
  [Input('uom-us-map', 'value')])
def update_chart(units):
  if units=='per100k':
    s = 0.1*county_sum['Conf100']
    t = county_sum['text100']
  else:
    s = 0.05*(county_sum['Confirmed'])
    t = county_sum['text']
  d= go.Scattergeo(
        lon = county_sum['Long_'],
        lat = county_sum['Lat'],
        text = t,
        hoverinfo = 'text',
        marker = dict(
                size = s,
                line_width=0.5,
                sizemode = 'area'
            ))
  fig6=go.Figure(data=d)
  fig6.update_layout(l_map)
  fig6.update_geos(scope="usa",
                lataxis_showgrid=False, 
                lonaxis_showgrid=False
                )
  return fig6


#Callbacks for RHS US charts

@app.callback(
  Output('us-trend-total', 'figure'),
  [Input('us-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_9(us_trend_cases)
  else:
    return make_fig_9(us_trend_deaths)

@app.callback(
  Output('us-cum-title', 'children'),
  [Input('us-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "Cumulative cases"
  else:
    return "Cumulative deaths"

@app.callback(
  Output('us-trend-new', 'figure'),
  [Input('us-new', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_10(us_newcases_cases)
  else:
    return make_fig_10(us_newcases_deaths)

@app.callback(
  Output('us-new-title', 'children'),
  [Input('us-new', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "New cases"
  else:
    return "New deaths"

#Callbacks for top15 states
@app.callback(
  Output('us-total', 'figure'),
  [Input('top-states', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_7_8(state_sum,"Confirmed")
  else:
    return make_fig_7_8(state_sum,"Deaths")

@app.callback(
  Output('us-capita', 'figure'),
  [Input('top-states', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_7_8(state_sum,"Conf100")
  else:
    return make_fig_7_8(state_sum,"Deaths100")

#Callback for UK map UoM
@app.callback(
  Output('UK map', 'figure'),
  [Input('uom-uk-map', 'value')])
def update_chart(units):
  if units == "Abs":
    s = 0.05*uk_scatter['Confirmed']
    t = uk_scatter['text']
  else:
    s = 0.2*uk_scatter['Conf100']
    t = uk_scatter['text100']
  d=go.Scattermapbox(
    lon = uk_scatter['long'],
    lat = uk_scatter['lat'],
    text = t,
    hoverinfo = 'text',
    marker = dict(
            size = s,
            sizemode = 'area',
        symbol = 'circle'
        ))
  fig11=go.Figure(data=d)
  fig11.update_layout(l_mapbox)
  return fig11

#Callbacks for RHS UK charts

@app.callback(
  Output('uk-trend-total', 'figure'),
  [Input('uk-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_14(eng_trend, wales_trend, scot_trend)
  else:
    fig = go.Figure(data=go.Bar(x=pd.to_datetime(world_data_deaths.columns),
                            y=world_data_deaths[world_data_deaths.index=="United Kingdom"].values[0]),
                          )
    fig.update_layout(barmode='stack')
    fig.update_layout(l_bar_s)
    return fig

@app.callback(
  Output('uk-cum-title', 'children'),
  [Input('uk-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "Cumulative cases (excl. Northern Ireland)"
  else:
    return "Cumulative deaths"

@app.callback(
  Output('uk-trend-new', 'figure'),
  [Input('uk-new', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_15(eng_trend, wales_trend, scot_trend)
  else:
    fig = go.Figure(data=go.Bar(x=pd.to_datetime(world_data_deaths.columns[:-1]),
                          y=world_data_deaths[world_data_deaths.index=="United Kingdom"].values[0][1:]-world_data_deaths[world_data_deaths.index=="United Kingdom"].values[0][:-1]),
                        )
    fig.update_layout(barmode='stack')
    fig.update_layout(l_bar_s)
    return fig

@app.callback(
  Output('uk-new-title', 'children'),
  [Input('uk-new', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "New cases (excl. Northern Ireland)"
  else:
    return "New deaths"

if __name__ == '__main__':
  app.run_server()