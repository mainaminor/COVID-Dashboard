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
#### DATA FOR WORLDWIDE ANALYSES ###############
################################################

continents=pd.read_csv("data/continents.csv").drop(columns="Unnamed: 0").replace({"United States of America": 'United States'})
df_p=pd.read_csv("data/worldpop.csv").set_index("Location").rename(index={"United States of America": 'United States'})
ctrs=pd.read_csv('data/countries.csv').set_index("name").rename(index={"United States of America": 'United States'})

################################################

url_1='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_2='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
df1=pd.read_csv(url_1)
df2=pd.read_csv(url_2)

################################################

def prep_world_data(df):
    df=df.groupby(by="Country/Region").sum()
    df.drop(labels=["Lat", "Long"], axis=1, inplace=True)
    df.loc[:,:str(df.columns[-1])]=np.clip(df.loc[:,:str(df.columns[-1])], a_min=0, a_max=None)
    df.rename(index={"US": 'United States'}, inplace=True)
    return df

world_data_cases= prep_world_data(df1)
world_data_deaths= prep_world_data(df2)

def prep_countries_data(d1,d2):
    d1=world_data_cases
    d2=world_data_deaths
    countries=ctrs.merge(d1[d1.columns[-1]], left_index=True, right_index=True)
    countries.rename(columns={d1.columns[-1]: "Confirmed"}, inplace=True)
    countries=countries.merge(d2[d2.columns[-1]], left_index=True, right_index=True)
    countries.rename(columns={d2.columns[-1]: "Deaths"}, inplace=True)
    countries=countries.merge(df_p["PopTotal"], left_index=True, right_index=True)
    countries["Conf100"]=round(countries["Confirmed"]*100/countries["PopTotal"])
    countries["Deaths100"]=round(countries["Deaths"]*100/countries["PopTotal"])
    countries["Mortality"]=round(countries["Deaths"]*100/countries["Confirmed"],2)
    countries["text"]= '<b>'+countries.index+'</b>'+'<br>' + "Cases: " + countries["Confirmed"].astype('str') + '<br>' + "Deaths: "+ countries["Deaths"].astype('str')
    countries["text100"]= countries.index +'<br>' + "Cases per 100k pop.: " + countries["Conf100"].astype('str') + '<br>' + "Deaths per 100k pop.: "+ countries["Deaths100"].astype('str')
    return countries   

countries_data= prep_countries_data(df1, df2)

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

def prep_reg_rolling_avg (d):
    d1=prep_region_trend(d)
    sr_7d=pd.DataFrame(index=d1.index,columns=list(d1.columns[7:]))
    for i in range(len(d1.columns)-7):
        f=(d1[d1.columns[i+7]]-d1[d1.columns[i]])/7
        sr_7d[sr_7d.columns[i]]=f
    return sr_7d

def prep_countries_daily():
    d1=prep_rolling_avg("cases")
    d2=prep_rolling_avg("deaths")
    countries=ctrs.merge(d1[d1.columns[-1]], left_index=True, right_index=True)
    countries.rename(columns={d1.columns[-1]: "Confirmed"}, inplace=True)
    countries=countries.merge(d2[d2.columns[-1]], left_index=True, right_index=True)
    countries.rename(columns={d2.columns[-1]: "Deaths"}, inplace=True)
    countries=countries.merge(df_p["PopTotal"], left_index=True, right_index=True)
    countries["Conf100"]=round(countries["Confirmed"]*100/countries["PopTotal"])
    countries["Deaths100"]=round(countries["Deaths"]*100/countries["PopTotal"])
    countries["Mortality"]=round(countries["Deaths"]*100/countries["Confirmed"],2)
    countries["text"]= '<b>'+countries.index+'</b>'+'<br>' + "New cases per day: "+ round(countries["Confirmed"],1).astype(int).astype(str) + '<br>New deaths per day: ' + round(countries['Deaths'],1).astype(int).astype(str)
    countries["text100"]= '<b>'+countries.index+'</b>' +'<br>' + "New cases daily: "+ + round(countries["Conf100"],1).astype(int).astype(str) + " per 100k pop."
    return countries

countries_daily = prep_countries_daily()

def prep_world_trend(scope):
    if scope == "cases":
      d=world_data_cases
    else:
      d=world_data_deaths
    world_trend=d.merge(continents, left_index=True, right_on="Country").groupby("Continent").sum()
    return world_trend


def prep_world_newcases(scope):
    if scope == "cases":
      df=prep_world_trend("cases")
    else:
      df=prep_world_trend("deaths")
    world_newcases=pd.DataFrame(index=df.index,columns=list(df.columns[1:]))
    for i in range(len(df.columns)-1):
        f=df[df.columns[i+1]]-df[df.columns[i]]
        world_newcases[world_newcases.columns[i]]=f
    return world_newcases

def prep_country_newcases(scope):
    if scope == "cases":
      df=world_data_cases
    else:
      df=world_data_deaths
    country_newcases=pd.DataFrame(index=df.index,columns=list(df.columns[1:]))
    for i in range(len(df.columns)-1):
        f=df[df.columns[i+1]]-df[df.columns[i]]
        country_newcases[country_newcases.columns[i]]=f
    return country_newcases   

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


try: 
  world_trend_cases= prep_world_trend("cases")
  world_trend_deaths= prep_world_trend("deaths")
  world_newcases_cases= prep_world_newcases("cases")
  world_newcases_deaths= prep_world_newcases("deaths")
  world_capita_cases= prep_world_capita("cases")
  world_capita_deaths= prep_world_capita("deaths")
  country_newcases_cases= prep_country_newcases("cases")
  country_newcases_deaths= prep_country_newcases("deaths")
  '''
  countries_data.to_csv("data/countries_data.csv")
  world_data_cases.to_csv("data/world_data_cases.csv")
  world_data_deaths.to_csv("data/world_data_deaths.csv")
  world_trend_cases.to_csv("data/world_trend_cases.csv")
  world_trend_deaths.to_csv("data/world_trend_deaths.csv")
  world_newcases_cases.to_csv("data/world_newcases_cases.csv")
  world_newcases_deaths.to_csv("data/world_newcases_deaths.csv")
  world_capita_cases.to_csv("data/world_capita_cases.csv")
  world_capita_deaths.to_csv("data/world_capita_deaths.csv")
  country_newcases_deaths.to_csv("data/country_newcases_deaths.csv")
  '''
except:
  pass
  '''
  countries_data=pd.read_csv("data/countries_data.csv").set_index("Unnamed: 0")
  world_data_cases=pd.read_csv("data/world_data_cases.csv").set_index("Country/Region")
  world_data_deaths=pd.read_csv("data/world_data_deaths.csv").set_index("Country/Region")  
  world_trend_cases=pd.read_csv("data/world_trend_cases.csv").set_index("Continent")
  world_trend_deaths=pd.read_csv("data/world_trend_deaths.csv").set_index("Continent")
  world_newcases_cases=pd.read_csv("data/world_newcases_cases.csv").set_index("Continent")
  world_newcases_deaths=pd.read_csv("data/world_newcases_deaths.csv").set_index("Continent")
  world_capita_cases=pd.read_csv("data/world_capita_cases.csv").set_index("Unnamed: 0")
  world_capita_deaths=pd.read_csv("data/world_capita_deaths.csv").set_index("Unnamed: 0")
  countries_newcases_cases=pd.read_csv("data/countries_newcases_cases.csv").set_index("Unnamed: 0")
  countries_newcases_deaths=pd.read_csv("data/countries_newcases_deaths.csv").set_index("Unnamed: 0")
  '''



options = [{'label':"World", 'value':"World"}]
for tic in world_data_cases.index:
  options.append({'label':tic, 'value':tic})



################################################
#### CHART LAYOUTS #############################
################################################

#WORLD & US MAPS
l_map=go.Layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    height=340,
    template="plotly_dark",
    paper_bgcolor = main_color,
    geo={
    'bgcolor': main_color,
    'visible': True, 
    'resolution':50, 
    'showcountries':True, 
    'countrycolor':country_border,
    'showlakes':False,
    'showsubunits':True, 
    'subunitcolor':country_border,
    'showframe':False,
    'coastlinecolor':country_border,
    'landcolor':"#202020"
    }
)


#WORLD BARS
l_bar_w=go.Layout(
  font= {'color': text_color_sub},
  height=265,
  template="plotly_dark",
  paper_bgcolor = main_color,
  plot_bgcolor = main_color,
  #width=90,
  margin={"r":5,"t":0,"l":0,"b":7},
  yaxis={"tickfont":{"size":9}},
  xaxis={"tickfont":{"size":9}},
  legend={'x':0.02, 'y':0.96, 'font':{'size':10}, 'itemclick': 'toggleothers'},
  dragmode=False
  )

#SIMPLE BARS
l_bar_s=go.Layout(
  font= {'color': text_color_sub},
  height=175,
  template="plotly_dark",
  paper_bgcolor = main_color,
  plot_bgcolor = main_color,
  margin={"r":5,"t":0,"l":0,"b":7},
  yaxis={"tickfont":{"size":9}},
  xaxis={"tickfont":{"size":9}},
  legend={'x':0.02, 'y':0.96, 'font':{'size':9}, 'itemclick': 'toggleothers'},
  dragmode=False
  )



#HIDE MODEBAR
conf = {'displayModeBar': False}

################################################
################ CHARTS ########################
################################################


#Reporting Area total cases

def make_fig_1(units):
  if units=="cum":
    map_data=countries_data
    size=0.0005
  else:
    map_data=countries_daily
    size=0.01

  d = go.Figure(go.Scattergeo(
      lon=map_data["longitude"],
      lat=map_data["latitude"],
      text = map_data['text'],
      hoverinfo = 'text',
      marker=dict(
          size= np.clip(size*map_data["Confirmed"],a_min=0, a_max=None),
          line_width=0.5,
          sizemode='area'
      )))
  fig1=go.Figure(data=d)
  fig1.update_layout(l_map)
  fig1.update_geos(projection_type="natural earth", lataxis_showgrid=False, lonaxis_showgrid=False,lataxis_range=[-60,85])
  return fig1

def make_fig_2_3(text):
    dat=countries_data
    fig = go.Figure(go.Bar(y=dat.sort_values(by=[text], ascending=True).index[-15:],
                          x=dat.sort_values(by=[text],ascending=True)[text][-15:],
                         orientation='h'
                        )
                 )
    fig.update_layout(l_bar_s)
    #fig.update_traces(marker={'color': main_color})
    return fig

def make_fig_2_3b(text):
    dat=countries_daily
    fig = go.Figure(go.Bar(y=dat.sort_values(by=[text], ascending=True).index[-15:],
                          x=dat.sort_values(by=[text],ascending=True)[text][-15:].round(0),
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
  fig.update_layout(l_bar_w)
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
  fig.update_layout(l_bar_w)
  return fig

#Country total cases
def make_fig_7_8(d, text):
  fig = go.Figure(go.Bar(y=d.sort_values(by=[text], ascending=True).index[-10:],
                          x=d.sort_values(by=[text],ascending=True)[text][-10:],
                         orientation='h'
                        )
                 )
  fig.update_layout(l_bar_s)
  return fig

#Timeseries
def make_time_series(df, area):
    dat=df
    fig = go.Figure(data=go.Bar(x=pd.to_datetime(np.array(dat.columns)),
                          y=dat.loc[area],
                        ))
    fig.update_layout(l_bar_w)
    return fig


##########################################
########  STYLES  ########################
##########################################

section_header = {'color':text_color_main, 'font-size': '1.5rem','background-color': "#181818", "margin-bottom":0}
section_subheader = {'font-size': '1.3rem', 'color': text_color_main,  'background-color': "#181818", 'margin-bottom':'1%'}
main_columns = {'paddingRight':'0%','paddingLeft':'0%'}
section_wrapper = {"padding": "2%"}
col_fill = {"background-color": "#181818"}


##########################################
#######  APP LAYOUT ######################
##########################################

layout = html.Div([
  html.Div([#row for world headers
    html.H5('Worldwide as of {}'.format(pd.to_datetime(world_data_cases.columns[-1]).strftime('%B %d, %Y')),
      style={'color':text_color_main, 'margin-bottom':0},
      ),       
    html.P('Data source: Johns Hopkins CSSE',
      style={'font-size': '1rem','color':text_color_sub, 'margin-bottom':0})
    ], 
    className='row subtitle', 
    style={'marginbottom':'15px','paddingTop':'1%','paddingBottom':'1%'},
    ),
  html.Div([#row for tiles
    html.Div([#four columns for cases
      html.P('Cases:', 
        style={'color':text_color_sub, 'font-size': '1.5rem', 'margin-bottom':'0%'}
        ),
      html.P('{}'.format(f'{world_data_cases[str(world_data_cases.columns[-1])].sum():,}'), 
        style={'color':'#FF8C00','font-size': '3rem','font-weight': 'bold','margin-bottom':'3%'}
        )
      ],
      className='four columns',
      style={'text-align': 'center'}
      ),
    html.Div([#four columns for deaths
      html.P('Deaths:', 
        style={'color':text_color_sub, 'font-size': '1.5rem', 'margin-bottom':'0%'}
        ),
      html.P('{}'.format(f'{world_data_deaths[str(world_data_deaths.columns[-1])].sum():,}'), 
        style={'color':'#FF8C00','font-size': '3rem','font-weight': 'bold','margin-bottom':'3%'}
        )
      ],
      className='four columns',
      style={'text-align': 'center'}
      ),
    html.Div([#four columns for mortality
      html.P('Avg mortality:', 
        style={'color':text_color_sub, 'font-size': '1.5rem', 'margin-bottom':'0%'}
        ),
      html.P('{} % '.format(round(100*world_data_deaths[str(world_data_deaths.columns[-1])].sum()/world_data_cases[str(world_data_cases.columns[-1])].sum(),1)), 
        style={'color':'#FF8C00','font-size': '3rem','font-weight': 'bold','margin-bottom':'3%'}
        )
      ], 
      className='four columns',
      style={'text-align': 'center'}
      ),
    ], 
    className='row flex-display', 
    ),
  html.Div([#row for world body
    html.Div([#seven columns for LHS
      html.Div([#row for world map
        html.Div([#row for world map header
          html.Div([#row for world header text
            html.H6('Spread by location',
              style = section_header,
              ),
            ],
            ),
          html.Div([#row for world header radio buttons
            dcc.RadioItems(
              id="uom-ww-map",
              options=[
              {'label': 'Daily', 'value': 'new'},
              {'label': 'Cumulative', 'value': 'cum'},
              ],
              value='new',
              labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
            ),
            ],
            style=section_subheader
            ),
          ], 
          className='row subtitle'
          ),
        html.Div([#row for world map chart
          dcc.Loading(
            dcc.Graph(id= "world", 
              #figure=make_fig_1("new"), 
              config=conf
              )
            ),
          html.P("Note: Daily numbers are the average of the most recent 7 days' data",
            style={'font-size': '1rem','color':text_color_sub, 'margin-bottom':0, 'paddingLeft':'1%'})
          ],
          className='row',
          style=col_fill
          ),
        ],
        className='row',
        style={'margin-bottom': "2%"}
        ),
      html.Div([#row for charts and headers
        html.Div([#row for headers
          html.Div([# row for text and radio buttons separation
            html.Div([# row for title text
              html.H6("Worst-hit countries", 
                style=section_header,
                ),
              ],
              ),
            html.Div([# row for radio buttons
              dcc.RadioItems(
                id="top-countries",
                options=[
                {'label': 'Daily', 'value': 'new'},
                {'label': 'Cumulative', 'value': 'cum'}
                ],
                value='new',
                labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
              )
              ],
              style=section_subheader
              ),
            ],
            className='row subtitle'
            ),
          ],
          className='row'
          ),
        html.Div([#row for charts
          html.Div([ # row for charts themselves
            html.Div([ # six columns for total
              html.Div([
                html.P('Cases',
                  style=section_subheader
                  ),
                dcc.Loading(
                  dcc.Graph(id='country-cases',
                    #figure=make_fig_2_3b("Confirmed"), 
                    config=conf
                    )
                  )
                ],
                style = section_wrapper
                ),
              ],
              className='six columns',
              style = section_subheader
              ),
            html.Div([#six columns for per100k
              html.Div([
                html.P('Deaths',
                  style=section_subheader
                  ),
                dcc.Loading(
                  dcc.Graph(id='country-deaths',
                    #figure=make_fig_2_3b("Deaths"), 
                    config=conf
                    )
                  )
                ],
                style = section_wrapper
                ),
              ],
              className='six columns',
              style = section_subheader
              ),
            html.P("Note: Daily numbers are the average of the most recent 7 days' data",
              style={'font-size': '1rem','color':text_color_sub, 'margin-bottom':0, 'paddingLeft':'1%'}
              )
            ],
            className='row',
            style={"background-color": main_color}
            ),
          ],
          className='row',
          style = {"margin-bottom": "2%"}
          ),
        ],
        className='row',
        ),
      ],
      className='six columns',
      ),
    html.Div([#five columns for RHS
      html.Div([#row for titles
        html.Div([#row for title text
          html.H6('Trend by Country',
            style = section_header,
            ),
          ],
          ),
        html.Div([#four columns for radio buttons
          dcc.RadioItems(
            id="world-cum",
            options=[
            {'label':  'Cases', 'value': 'Cases'},
            {'label': 'Deaths', 'value': 'Deaths'}],
            value='Cases',
            labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
            )
          ],
          style=section_subheader
          ),
        html.Div([
          dcc.Dropdown(
            id="world-selector",
            options=options,
            value ='World',
            multi = False,
            ),
          ], 
          className="row",
          style={'color': text_color_main,  'background-color': main_color, 'margin-bottom':0, 'margin-top':'1%','padding': '0%'}
          ),
        ],
        className="row subtitle"
        ),
      html.Div([# div for dropdown wrapper
        html.Div([# row for new cases
          html.Div([#row for new cases headers
            html.Div([#row for text
              html.P(id='world-new-title', 
                style=section_subheader
                ),
              ], 
              className="eight columns"
              ),
            ],
            className='row'
            ),
          html.Div([#row for new cases graph
            dcc.Loading(
              dcc.Graph(id='world-trend-new', 
                #figure=make_fig_5(world_newcases_cases), 
                config=conf
                ) 
              ),
            ],
            className='row',
            ),  
          ],
          className='row',
          style=section_wrapper
          ),
        html.Div([#row for cumulative cases
          html.Div([# row for cumulative cases headers
            html.Div([#eight columns for header text
              html.P(id='world-cum-title',
                style=section_subheader
                )
              ], 
              className="eight columns"
              ),    
            ],
            className='row'
            ),
          html.Div([#row for cumulative cases graph
            dcc.Loading(
              dcc.Graph(id='world-trend-cum',
                  #figure=make_fig_4(world_trend_cases), 
                  config=conf
                  )
              )
            ],
            className='row',
            ),
          ],
          className='row',
          style=section_wrapper
          ),
        ],
        style = col_fill
        )
      ],
      className='six columns',
      ),
    ],
    className='row'
    ),
],
style={"padding": "0%"}
)

################################################
#### APP CALLBACKS  ############################
################################################


#Callback for world map UoM
@app.callback(
  Output('world', 'figure'),
  [Input('uom-ww-map', 'value')])
def update_chart(units):
  return make_fig_1(units)

#Callbacks for RHS World charts

@app.callback(
  Output('world-trend-cum', 'figure'),
  [Input('world-cum', 'value'),
  Input('world-selector', 'value')
  ])

def update_chart(trend, scope):
  if trend == 'Cases':
    if scope =="World":
      return make_fig_4(world_trend_cases)
    else:
      return make_time_series(world_data_cases, scope)
  else:
    if scope == "World":
      return make_fig_4(world_trend_deaths)
    else:
      return make_time_series(world_data_deaths, scope)

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
  [Input('world-cum', 'value'),
  Input('world-selector', 'value')
  ])

def update_chart(trend, scope):
  if trend == 'Cases':
    if scope =="World":
      return make_fig_5(world_newcases_cases)
    else:
      return make_time_series(country_newcases_cases, scope)
  else:
    if scope == "World":
      return make_fig_5(world_newcases_deaths)
    else:
      return make_time_series(country_newcases_deaths, scope)

@app.callback(
  Output('world-new-title', 'children'),
  [Input('world-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "New cases"
  else:
    return "New deaths"

#Callbacks for top15 countries
@app.callback(
  Output('country-cases', 'figure'),
  [Input('top-countries', 'value')])

def update_chart(trend):
  if trend == 'cum':
    return make_fig_2_3("Confirmed")
  else:
    return make_fig_2_3b("Confirmed")

@app.callback(
  Output('country-deaths', 'figure'),
  [Input('top-countries', 'value')])

def update_chart(trend):
  if trend == 'cum':
    return make_fig_2_3("Deaths")
  else:
    return make_fig_2_3b("Deaths")