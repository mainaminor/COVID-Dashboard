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
#### DATA FOR USA ANALYSES #####################
################################################

url_3='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
url_4='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
url_5='https://raw.githubusercontent.com/cphalpert/census-regions/master/us%20census%20bureau%20regions%20and%20divisions.csv'

df3=pd.read_csv(url_3)
df4=pd.read_csv(url_4).drop("Population", axis=1)
us_regions=pd.read_csv('data/us_regions.csv').drop(columns="Unnamed: 0")
us_pop=pd.read_csv('data/us_pop.csv')

def prep_county_data(d):
    df=d.drop(labels=["UID","iso2", "iso3","Province_State","Country_Region"], axis=1)
    df.drop(df[df["Admin2"].isnull()].index, inplace=True)
    df.drop(df[df["FIPS"].isnull()].index, inplace=True)
    return df
county_data_cases = prep_county_data(df3)
county_data_deaths = prep_county_data(df4) 

def prep_state_data(d):
    df=d.groupby(by="Province_State").sum()
    df.rename(index={"District of Columbia": "D.C."}, inplace=True)
    df.drop(labels=["UID", "code3", "FIPS", "Lat", "Long_"], axis=1, inplace=True)
    df.loc[:,:str(df.columns[-1])]=np.clip(df.loc[:,:str(df.columns[-1])], a_min=0, a_max=None)
    return df
state_data_cases= prep_state_data(df3)
state_data_deaths= prep_state_data(df4)

def prep_cty_daily_trend (scope):
    if scope == "cases":
      d1=county_data_cases.drop(columns=["code3", "FIPS", "Lat", "Long_"]).groupby(by="Combined_Key").sum()
    else:
      d1=county_data_deaths.drop(columns=["code3", "FIPS", "Lat", "Long_"]).groupby(by="Combined_Key").sum()
    sr_1d=pd.DataFrame(index=d1.index,columns=list(d1.columns[1:]))
    for i in range(len(d1.columns)-1):
        f=(d1[d1.columns[i+1]]-d1[d1.columns[i]])/1
        sr_1d[sr_1d.columns[i]]=f
    return sr_1d

def prep_cty_rolling_avg (scope):
    if scope == "cases":
      d1=county_data_cases.drop(columns=["code3", "FIPS", "Lat", "Long_"]).groupby(by="Combined_Key").sum()
    else:
      d1=county_data_deaths.drop(columns=["code3", "FIPS", "Lat", "Long_"]).groupby(by="Combined_Key").sum()
    sr_7d=pd.DataFrame(index=d1.index,columns=list(d1.columns[7:]))
    for i in range(len(d1.columns)-7):
        f=(d1[d1.columns[i+7]]-d1[d1.columns[i]])/7
        sr_7d[sr_7d.columns[i]]=f
    return sr_7d

def prep_county_sum():
    dd1=county_data_cases
    dd2=county_data_deaths
    df=dd1[["Admin2", "FIPS", "Lat", "Long_", dd1.columns[-1]]]
    df=df.rename(columns={dd1.columns[-1]: "Confirmed"})
    df=df.merge(dd2[["FIPS",dd2.columns[-1]]], on="FIPS")
    df=df.rename(columns={dd2.columns[-1]: "Deaths"})
    df=df.merge(us_pop[["FIPS", "STNAME","CTYNAME", "POPESTIMATE2019", "Abbreviation"]], on="FIPS")
    df["Mortality"]=round(df["Deaths"]*100/df["Confirmed"],2)
    df["Conf100"]=df["Confirmed"]*100000/df["POPESTIMATE2019"]
    df["Deaths100"]=df["Deaths"]*100000/df["POPESTIMATE2019"]
    df["Ctylabel"]=df["Admin2"]+ ", "+df["Abbreviation"]
    df["text"]= '<b>'+df["Ctylabel"]+'</b>' + '<br>Cases: ' + (round(df['Confirmed'],1).astype(int).astype(str))+ '<br>Deaths: ' + (round(df['Deaths'],1).astype(int).astype(str))
    df["text100"]= df["Ctylabel"] + '<br>Cases per 100k pop: ' + (round(df['Conf100'],1).astype(str))+ '<br>Deaths per 100k pop: ' + (round(df['Deaths100'],1).astype(str))
    return df
county_sum = prep_county_sum()

def prep_county_daily():
    dd1=prep_cty_rolling_avg("cases")
    dd2=prep_cty_rolling_avg("deaths")
    df=county_data_cases[["Admin2", "FIPS", "Lat", "Long_", "Combined_Key"]].merge(dd1[dd1.columns[-1]], how="right", right_index=True, left_on="Combined_Key")
    df=df.rename(columns={dd1.columns[-1]: "Confirmed"})
    df=df.merge(dd2[dd2.columns[-1]], left_on="Combined_Key", right_index=True)
    df=df.rename(columns={dd2.columns[-1]: "Deaths"})
    df=df.merge(us_pop[["FIPS", "STNAME","CTYNAME", "POPESTIMATE2019", "Abbreviation"]], on="FIPS")
    df["Mortality"]=round(df["Deaths"]*100/df["Confirmed"],2)
    df["Conf100"]=df["Confirmed"]*100000/df["POPESTIMATE2019"]
    df["Deaths100"]=df["Deaths"]*100000/df["POPESTIMATE2019"]
    df["Ctylabel"]=df["Admin2"]+ ", "+df["Abbreviation"]
    df["text"]= '<b>'+df["Ctylabel"]+'</b>' + '<br>New cases per day: ' + round(df['Confirmed'],1).astype(int).astype(str) + '<br>New deaths per day: ' + round(df['Deaths'],1).astype(int).astype(str)
    df["text100"]= df["Ctylabel"] + '<br>New cases day: ' + (round(df['Conf100'],1).astype(int).astype(str))+ ' per 100k pop'
    return df

def prep_state_sum():
    df=county_sum
    df=df[["STNAME", "Confirmed", "Deaths", "POPESTIMATE2019"]].groupby("STNAME").sum()
    df.rename(index={"District of Columbia": "D.C."}, inplace=True)
    df["Conf100"]=df["Confirmed"]*100000/df["POPESTIMATE2019"]
    df["Deaths100"]=df["Deaths"]*100000/df["POPESTIMATE2019"]
    df["Mortality"]=round(df["Deaths"]*100/df["Confirmed"],2)
    return df

def prep_us_trend(scope):
    if scope == "cases":
      df = state_data_cases
    else:
      df = state_data_deaths
    df=df.merge(us_regions, left_index=True, right_on="State")
    df=df.groupby("Region").sum()
    return df

def prep_us_newcases(scope):
    df=prep_us_trend(scope)
    dff=pd.DataFrame(index=df.index,columns=list(df.columns[1:]))
    for i in range(len(df.columns)-1):
        f=df[df.columns[i+1]]-df[df.columns[i]]
        dff[dff.columns[i]]=f
    return dff

def prep_state_newcases(scope):
    if scope == "cases":
      df = state_data_cases
    else:
      df = state_data_deaths
    dff=pd.DataFrame(index=df.index,columns=list(df.columns[1:]))
    for i in range(len(df.columns)-1):
        f=df[df.columns[i+1]]-df[df.columns[i]]
        dff[dff.columns[i]]=f
    return dff

def prep_state_daily():
    df=prep_county_daily()
    df=df[["STNAME", "Confirmed", "Deaths", "POPESTIMATE2019"]].groupby("STNAME").sum()
    df.rename(index={"District of Columbia": "D.C."}, inplace=True)
    df["Conf100"]=df["Confirmed"]*100000/df["POPESTIMATE2019"]
    df["Deaths100"]=df["Deaths"]*100000/df["POPESTIMATE2019"]
    df["Mortality"]=round(df["Deaths"]*100/df["Confirmed"],2)
    return df

def prep_cty_daily_trend (scope):
    if scope == "cases":
      d1=county_data_cases.drop(columns=["code3", "FIPS", "Lat", "Long_"]).groupby(by="Combined_Key").sum()
    else:
      d1=county_data_deaths.drop(columns=["code3", "FIPS", "Lat", "Long_"]).groupby(by="Combined_Key").sum()
    sr_1d=pd.DataFrame(index=d1.index,columns=list(d1.columns[1:]))
    for i in range(len(d1.columns)-1):
        f=(d1[d1.columns[i+1]]-d1[d1.columns[i]])/1
        sr_1d[sr_1d.columns[i]]=f
    return sr_1d

try:
  
  state_sum= prep_state_sum()
  us_trend_cases= prep_us_trend("cases")
  us_trend_deaths= prep_us_trend("deaths")
  us_newcases_cases= prep_us_newcases("cases")
  us_newcases_deaths= prep_us_newcases("deaths")
  state_newcases_cases=prep_state_newcases("cases")
  state_newcases_deaths=prep_state_newcases("deaths")
  '''
  county_data_cases.to_csv("data/county_data_cases.csv")
  county_data_deaths.to_csv("data/county_data_deaths.csv")
  state_data_cases.to_csv("data/state_data_cases.csv")
  state_data_deaths.to_csv("data/state_data_deaths.csv")
  county_sum.to_csv("data/county_sum.csv")
  state_sum.to_csv("data/state_sum.csv")
  us_trend_cases.to_csv("data/us_trend_cases.csv")
  us_trend_deaths.to_csv("data/us_trend_deaths.csv")
  us_newcases_cases.to_csv("data/us_newcases_cases.csv")
  us_newcases_deaths.to_csv("data/us_newcases_deaths.csv")
  state_newcases_cases.to_csv("data/state_newcases_cases")
  state_newcases_deaths.to_csv("data/state_newcases_deaths")
  '''
except:
  pass
  '''
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
  state_newcases_cases=pd.read_csv("data/state_newcases_cases.csv").drop(columns="Unnamed: 0")
  state_newcases_deaths=pd.read_csv("data/state_newcases_deaths.csv").drop(columns="Unnamed: 0")
  '''

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
  height=268,
  template="plotly_dark",
  paper_bgcolor = main_color,
  plot_bgcolor = main_color,
  #width=90,
  margin={"r":5,"t":0,"l":0,"b":7},
  yaxis={"tickfont":{"size":10}},
  xaxis={"tickfont":{"size":10}},
  legend={'x':0.02, 'y':0.96, 'font':{'size':10}, 'itemclick': 'toggleothers'},
  dragmode=False
  )



#SIMPLE BARS
l_bar_s=go.Layout(
  height=175,
  margin={"r":5,"t":0,"l":0,"b":7},
  template="plotly_dark",
  paper_bgcolor = main_color,
  plot_bgcolor = main_color,
  yaxis={"tickfont":{"size":9}},
  xaxis={"tickfont":{"size":9}},
  legend={'x':0.02, 'y':0.96, 'font':{'size':9}, 'itemclick': 'toggleothers'},
  dragmode=False
  )

#HIDE MODEBAR
conf = {'displayModeBar': False}

#Country map

def make_map(units):
  if units=='cum':
    map_data=prep_county_sum()
    s=0.005
  else:
    map_data=prep_county_daily()
    s=0.1
  d= go.Scattergeo(
          lon = map_data['Long_'],
          lat = map_data['Lat'],
          text = map_data['text'],
          hoverinfo = 'text',
          marker = dict(
                  size = s*np.clip(map_data['Confirmed'],a_min=0, a_max=None),
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
#County total cases
def make_fig_7_8(d, text):
    fig = go.Figure(go.Bar(y=d.sort_values(by=[text], ascending=True)["Ctylabel"][-15:],
                          x=d.sort_values(by=[text],ascending=True)[text][-15:].round(0),
                         orientation='h'
                        )
                 )
    fig.update_layout(l_bar_s)
    return fig

def make_fig_7_8b(text):
    data=prep_state_daily()
    fig = go.Figure(go.Bar(y=data.sort_values(by=[text], ascending=True).index[-15:],
                          x=data.sort_values(by=[text],ascending=True)[text][-15:].round(0),
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
  fig.update_layout(l_bar_w)
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
  fig.update_layout(l_bar_w)
  return fig

def make_fig_11(text):
    dat=prep_state_sum()
    fig = go.Figure(go.Bar(y=dat.sort_values(by=[text], ascending=True).index[-15:],
                          x=dat.sort_values(by=[text],ascending=True)[text][-15:].round(0),
                         orientation='h'
                        )
                 )
    fig.update_layout(l_bar_s)
    return fig


def make_time_series(scope, area):
    if scope == "cases":
      dat=county_data_cases.groupby(by="Combined_Key").sum().drop(["code3", "FIPS", "Lat", "Long_"], axis=1)
    else:
      dat=county_data_deaths.groupby(by="Combined_Key").sum().drop(["code3", "FIPS", "Lat", "Long_"], axis=1)
    fig = go.Figure(data=go.Bar(x=pd.to_datetime(np.array(dat.columns)),
                          y=dat.loc[area],
                        ))
    fig.update_layout(l_bar_w)
    return fig

def make_time_series_new(scope, area):
    dat=prep_cty_daily_trend(scope)
    fig = go.Figure(data=go.Bar(x=pd.to_datetime(np.array(dat.columns)),
                          y=dat.loc[area],
                        ))
    fig.update_layout(l_bar_w)
    return fig


cty_list = [{'label':"United States", 'value':"United States"}]
for tic in list(df3["Combined_Key"].drop_duplicates().sort_values()):
  cty_list.append({'label':tic, 'value':tic})


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
  html.Div([#row for US header
    html.H5('United States as of {}'.format(pd.to_datetime(df3.columns[-1]).strftime('%B %d, %Y')),
      style={"color":text_color_main, 'margin-bottom':0}
      ),       
    html.P('Data source: Johns Hopkins CSSE',
      style={'font-size': '1rem','color':'#696969', 'color': text_color_sub, 'margin-bottom':0})
    ], 
    className='row subtitle', 
    style={'marginbottom':'15px','paddingTop':'1%','paddingBottom':'1%'},
    ),
  html.Div([#row for tiles
    html.Div([#cases
      html.P('Cases:',
        style={'color':text_color_main, 'font-size': '1.5rem', 'margin-bottom':'0%'}
        ),
      html.P('{}'.format(f'{df3.iloc[:,-1].sum():,}'), 
        style={'color':'#FF8C00','font-size': '3rem','font-weight': 'bold','margin-bottom':'3%'}
        )
      ],
      className='four columns',
      style={'text-align': 'center'}
      ),
    html.Div([#deaths
      html.P('Deaths:',
        style={'color':text_color_main, 'font-size': '1.5rem', 'margin-bottom':'0%'}
        ),
      html.P('{}'.format(f'{df4.iloc[:,-1].sum():,}'),
        style={'color':'#FF8C00','font-size': '3rem','font-weight': 'bold','margin-bottom':'3%'}
        )
      ],
      className='four columns',
      style={'text-align': 'center'}
      ),
    html.Div([#mortality
      html.P('Avg mortality:', 
        style={'color':text_color_main, 'font-size': '1.5rem', 'margin-bottom':'0%'}
        ),
      html.P('{} % '.format(round(100*df4.iloc[:,-1].sum()/df3.iloc[:,-1].sum(),1)), 
        style={'color':'#FF8C00','font-size': '3rem','font-weight': 'bold','margin-bottom':'3%'}
        )
      ],
      className='four columns',
      style={'text-align': 'center'}
      ),
    ],
    className='row', 
    ),
  html.Div([#row for US body
    html.Div([#seven columns for LHS
      html.Div([#row for US map
        html.Div([# row for US map titles
          html.Div([#title text
            html.H6('Spread by location',
              style = section_header,
              ),
            ],
            className='row'
            ),
          html.Div([#radio items
            dcc.RadioItems(
              id="uom-us-map",
              options=[
              {'label': 'Daily', 'value': 'new'},
              {'label': 'Cumulative', 'value': 'cum'}
              ],
              value='new',
              labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
              ),
            ], 
            style=section_subheader
            )
          ], 
          className='row subtitle'
          ),
        html.Div([#row for US map itself
          dcc.Loading(
            dcc.Graph(id= "US map",
              #figure=make_map("Abs"),
              config=conf
              ),
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
      html.Div([#row for bar charts
        html.Div([#row for titles
            html.Div([#eight columns for text
              html.H6("Worst-hit areas",
                style = section_header
                )
              ], 
              className='row'
              ),
            html.Div([#four columns for radio buttons
              dcc.RadioItems(
                id="top-states",
                options=[
                {'label': 'Daily', 'value': 'new'},
                {'label':  'Cumulative', 'value': 'cum'}               
                ],
                value='new',
                labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
              ),
              ],
              className="row",
              style = section_subheader
              ),
            ],
            className='row subtitle'
            ),
        html.Div([#row for charts
          html.Div([#six columns for county
            html.P('By county',
              style=section_subheader
              ),
            dcc.Loading(
              dcc.Graph(id='us-county', 
                #figure=make_fig_7_8(prep_county_daily(), "Confirmed"), 
                config=conf
                ),
              ),
            ], 
            className="six columns",
            style = section_wrapper
            ),
          html.Div([#six columns for state
            html.P('By state',
              style=section_subheader
              ),
            dcc.Loading(
              dcc.Graph(id='us-state',
                #figure=make_fig_7_8b("Confirmed"), 
                config=conf
                )
              ),
            ],
            className='six columns',
            style = section_wrapper
            ),      
          html.P("Note: Daily numbers are the average of the most recent 7 days' data",
            style={'font-size': '1rem','color':text_color_sub, 'margin-bottom':0, 'paddingLeft':'1%'})
          ],
          className='row',
          style=section_subheader
          ),
        ],
        className='row',
        style = {"margin-bottom": "2%"}
        ),
      ],
      className='six columns',
      ),
    html.Div([#five columns for RHS
      html.Div([
        html.Div([#title text
          html.H6('Trend by US County',
            style = section_header
            ),
          ],
          className='row'
          ),
        html.Div([#four columns for radio items
          dcc.RadioItems(
            id="us-cum",
            options=[
            {'label':  'Cases', 'value': 'Cases'},
            {'label': 'Deaths', 'value': 'Deaths'}],
            value='Cases',
            labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
          )
          ],
          className="row",
          style=section_subheader
          ),
        html.Div([# dropdown
          dcc.Dropdown(
            id="US-selector",
            options=cty_list,
            value ='United States',
            multi = False,
            ),
          ], 
          className="row",
          style={'color': text_color_main,  'background-color': main_color, 'margin-bottom':0, 'margin-top':'1%','padding': '0%'}
          ),
        ],
        className="row subtitle"
        ),
      html.Div([ # row for wrapper  
        html.Div([#row for new cases
          html.Div([#row for titles
            html.Div([#row for text
              html.P(id='us-new-title',
                style=section_subheader
                ),
              ], 
              className="row"
              ),
            ],
            className='row'
            ),
          html.Div([#row for chart itself
            dcc.Loading(
              dcc.Graph(id='us-trend-new', 
                #figure=make_fig_10(us_newcases_cases), 
                config=conf
                ),
              ),
            ],
            className='row'
            ),
          ],
          className='row',
          style=section_wrapper
          ),
        html.Div([#row for cum cases
          html.Div([#row for titles
            html.Div([#eight columns for text
              html.P(id='us-cum-title',
                style=section_subheader
                ),
              ], 
              className="row"
              ),
            ],
            className='row'
            ),
          html.Div([#row for chart itself
            dcc.Loading(
              dcc.Graph(id='us-trend-total', 
                #figure=make_fig_9(us_trend_cases), 
                config=conf
                ),
              ),
            ],
            className='row'
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

#Callback for US map UoM
@app.callback(
  Output('US map', 'figure'),
  [Input('uom-us-map', 'value')])
def update_chart(units):
  return make_map(units)

#Callbacks for RHS US charts

@app.callback(
  Output('us-trend-total', 'figure'),
  [Input('us-cum', 'value'),
  Input('US-selector', 'value')
  ])

def update_chart(trend, scope):
  if trend == 'Cases':
    if scope == "United States":
      return make_fig_9(us_trend_cases)
    else:
      return make_time_series("cases", scope)
  else:
    if scope == "United States":
      return make_fig_9(us_trend_deaths)
    else:
      return make_time_series("deaths", scope)

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
  [Input('us-cum', 'value'),
  Input('US-selector', 'value')
  ])

def update_chart(trend,scope):
  if trend == 'Cases':
    if scope == "United States":
      return make_fig_10(us_newcases_cases)
    else:
      return make_time_series_new("cases", scope)
  else:
    if scope == "United States":
      return make_fig_10(us_newcases_deaths)
    else:
      return make_time_series_new("deaths", scope)


@app.callback(
  Output('us-new-title', 'children'),
  [Input('us-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "New cases"
  else:
    return "New deaths"

#Callbacks for top15 states
@app.callback(
  Output('us-county', 'figure'),
  [Input('top-states', 'value')])

def update_chart(trend):
  if trend == 'cum':
    return make_fig_7_8(prep_county_sum(),"Confirmed")
  else:
    return make_fig_7_8(prep_county_daily(), "Confirmed")

@app.callback(
  Output('us-state', 'figure'),
  [Input('top-states', 'value')])

def update_chart(trend):
  if trend == 'cum':
    return make_fig_11("Confirmed")
  else:
    return make_fig_7_8b("Confirmed")