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

df1=pd.read_csv("data/df1.csv").drop("Unnamed: 0", axis=1)
df2=pd.read_csv("data/df2.csv").drop("Unnamed: 0", axis=1)

ctrs=pd.read_csv('data/countries.csv').set_index("name")
continents=pd.read_csv("data/continents.csv").drop(columns="Unnamed: 0")

df_p=pd.read_csv("data/worldpop.csv").set_index("Location")



#################################################

def prep_world_data(df):
  df=df.groupby(by="Country/Region").sum()
  df.drop(labels=["Lat", "Long"], axis=1, inplace=True)
  df.loc[:,:str(df.columns[-1])]=np.clip(df.loc[:,:str(df.columns[-1])], a_min=0, a_max=None)
  df.rename(index={"US": 'United States of America'}, inplace=True)
  return df

def prep_countries_data(d1,d2):
  d1=prep_world_data(d1)
  d2=prep_world_data(d2)
  countries=ctrs.merge(d1[d1.columns[-1]], left_index=True, right_index=True)
  countries.rename(columns={d1.columns[-1]: "Confirmed"}, inplace=True)
  countries=countries.merge(d2[d2.columns[-1]], left_index=True, right_index=True)
  countries.rename(columns={d2.columns[-1]: "Deaths"}, inplace=True)
  countries=countries.merge(df_p["PopTotal"], left_index=True, right_index=True)
  countries["Conf100"]=round(countries["Confirmed"]*100/countries["PopTotal"])
  countries["Deaths100"]=round(countries["Deaths"]*100/countries["PopTotal"])
  countries["Mortality"]=round(countries["Deaths"]*100/countries["Confirmed"],2)
  countries["text"]= countries.index +'<br>' + "Cases: " + countries["Confirmed"].astype('str') + '<br>' + "Deaths: "+ countries["Deaths"].astype('str')
  countries["text100"]= countries.index +'<br>' + "Cases per 100k pop.: " + countries["Conf100"].astype('str') + '<br>' + "Deaths per 100k pop.: "+ countries["Deaths100"].astype('str')
  return countries

def prep_world_trend(d):
  d=prep_world_data(d)
  world_trend=d.merge(continents, left_index=True, right_on="Country").groupby("Continent").sum()
  return world_trend

def prep_world_newcases(d):
  df=prep_world_trend(d)
  world_newcases=pd.DataFrame(index=df.index,columns=list(df.columns[1:]))
  for i in range(len(df.columns)-1):
    f=df[df.columns[i+1]]-df[df.columns[i]]
    world_newcases[world_newcases.columns[i]]=f
  return world_newcases

def prep_world_capita (d):
    d1=prep_world_data(d)
    t=d1.merge(df_p, left_index=True, right_index=True)
    a=t.loc[:, :d1.columns[-1]].values.transpose()
    b=100/t["PopTotal"].values
    c=a*b
    t.loc[:, :d1.columns[-1]]=c.transpose()
    return t

def prep_rolling_avg(d):
  d1=prep_world_capita(d)
  d11=prep_world_data(d)
  sr_5d=pd.DataFrame(index=d1.index,columns=list(d11.columns[5:]))
  for i in range(len(d11.columns)-5):
      f=(d1[d1.columns[i+5]]-d1[d1.columns[i]])/5
      sr_5d[sr_5d.columns[i]]=f
  return sr_5d

options = []
for tic in prep_countries_data(df1,df2).index:
  options.append({'label':tic, 'value':tic})


################################################
#### DATA FOR USA ANALYSES #####################
################################################

df3=pd.read_csv('data/df3.csv').drop("Unnamed: 0", axis=1)
df4=pd.read_csv('data/df4.csv').drop("Unnamed: 0", axis=1)
us_regions=pd.read_csv('data/us_regions.csv').drop("Unnamed: 0", axis=1)
us_pop=pd.read_csv('data/us_pop.csv')

def prep_county_data(d):
    df=d.drop(labels=["UID","iso2", "iso3","Province_State","Country_Region"], axis=1)
    df.drop(df[df["Admin2"].isnull()].index, inplace=True)
    df.drop(df[df["FIPS"].isnull()].index, inplace=True)
    return df   

def prep_state_data(d):
    df=d.groupby(by="Province_State").sum()
    df.drop(labels=["UID", "code3", "FIPS", "Lat", "Long_"], axis=1, inplace=True)
    df.loc[:,:str(df.columns[-1])]=np.clip(df.loc[:,:str(df.columns[-1])], a_min=0, a_max=None)
    return df

def prep_county_sum(d1,d2):
    dd1=prep_county_data(d1)
    dd2=prep_county_data(d2)
    df=dd1[["Admin2", "FIPS", "Lat", "Long_", dd1.columns[-1]]]
    df=df.rename(columns={dd1.columns[-1]: "Confirmed"})
    df=df.merge(dd2[["FIPS",dd2.columns[-1]]], on="FIPS")
    df=df.rename(columns={dd2.columns[-1]: "Deaths"})
    df=df.merge(us_pop[["FIPS", "STNAME","CTYNAME", "POPESTIMATE2019", "Abbreviation"]], on="FIPS")
    df["Mortality"]=round(df["Deaths"]*100/df["Confirmed"],2)
    df["Conf100"]=df["Confirmed"]*100000/df["POPESTIMATE2019"]
    df["Deaths100"]=df["Deaths"]*100000/df["POPESTIMATE2019"]
    df["Ctylabel"]=df["Admin2"]+ ", "+df["Abbreviation"]
    df["text"]= df["Ctylabel"] + '<br>Cases: ' + (round(df['Confirmed'],1).astype(str))+ '<br>Deaths: ' + (round(df['Deaths'],1).astype(str))
    df["text100"]= df["Ctylabel"] + '<br>Cases per 100k pop: ' + (round(df['Conf100'],1).astype(str))+ '<br>Deaths per 100k pop: ' + (round(df['Deaths100'],1).astype(str))
    return df


def prep_state_sum(d1,d2):
    df=prep_county_sum(d1,d2)
    df=df[["STNAME", "Confirmed", "Deaths", "POPESTIMATE2019"]].groupby("STNAME").sum()
    df["Conf100"]=df["Confirmed"]*100000/df["POPESTIMATE2019"]
    df["Deaths100"]=df["Deaths"]*100000/df["POPESTIMATE2019"]
    df["Mortality"]=round(df["Deaths"]*100/df["Confirmed"],2)
    return df

def prep_us_trend(d):
    df=prep_state_data(d)
    df=df.merge(us_regions, left_index=True, right_on="State")
    df=df.groupby("Region").sum()
    return df

def prep_us_newcases(d):
    df=prep_us_trend(d)
    dff=pd.DataFrame(index=df.index,columns=list(df.columns[1:]))
    for i in range(len(df.columns)-1):
        f=df[df.columns[i+1]]-df[df.columns[i]]
        dff[dff.columns[i]]=f
    return dff


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

def convert(val):
    step1=str(val)
    step2 = step1.replace(',','')
    step3 = step2.replace('**','')
    step4= int(step3)
    return step4

def prep_uk_scatter(d1,d2,d3):
    dd1=d1.drop(d1[d1["Area type"]=="Region"].index)
    dd1=dd1[["Area name", "Specimen date", "Cumulative lab-confirmed cases"]][dd1["Specimen date"]==dd1["Specimen date"].max()]
    dd1=dd1.drop(labels=["Specimen date"], axis=1)
    dd1.rename(columns={"Area name":"ReportingArea", "Cumulative lab-confirmed cases": "Confirmed"}, inplace=True)
    dd2=d2[d2["Specimen date"]==d2["Specimen date"].max()][["Local Authority", "Cumulative cases"]].rename(columns={"Local Authority": "ReportingArea", "Cumulative cases": "Confirmed"})
    df=dd1.append(dd2, ignore_index=True).append(d3, ignore_index=True)
    df=df.astype('str')
    df.set_index("ReportingArea", inplace=True)
    df=df.merge(uk_pop, right_index=True, left_index=True).merge(uk_map, on="ReportingArea")
    df["Confirmed"]=df["Confirmed"].apply(convert)
    df["Conf100"]=round(df["Confirmed"]*100000/df["All ages"])
    df["text"]= df.index+ ', '+ '<br>Cases: ' + (df['Confirmed']).astype(str)
    df["text100"]= df.index + ', '+ '<br>Cases per 100k pop: ' + (round(df['Conf100'],1).astype(str))
    return df



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
    #'projection_type': "natural earth",
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

#HIDE MODEBAR
conf = {'displayModeBar': False}


################################################
################ CHARTS ########################
################################################


#Reporting Area total cases

def make_fig_2_3(d1,d2,text):
  fig = go.Figure(go.Bar(y=prep_countries_data(d1,d2).sort_values(by=[text], ascending=True).index[-15:],
                          x=prep_countries_data(d1,d2).sort_values(by=[text],ascending=True)[text][-15:],
                         orientation='h'
                        )
                 )
  fig.update_layout(l_bar_s)
  return fig

#Cumulative cases by continent

def make_fig_4(d):
  fig = go.Figure(data=[go.Bar(x=pd.to_datetime(np.array(prep_world_trend(d).columns)),
                          y=prep_world_trend(d).iloc[0],
                          name=prep_world_trend(d).index[0]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_trend(d).columns)),
                          y=prep_world_trend(d).iloc[1],
                          name=prep_world_trend(d).index[1]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_trend(d).columns)),
                          y=prep_world_trend(d).iloc[2],
                          name=prep_world_trend(d).index[2]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_trend(d).columns)),
                          y=prep_world_trend(d).iloc[3],
                          name=prep_world_trend(d).index[3]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_trend(d).columns)),
                          y=prep_world_trend(d).iloc[4],
                          name=prep_world_trend(d).index[4]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_trend(d).columns)),
                          y=prep_world_trend(d).iloc[5],
                          name=prep_world_trend(d).index[5])]
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig


#Trend new cases by continent
def make_fig_5(d):
  fig = go.Figure(data=[go.Bar(x=pd.to_datetime(np.array(prep_world_newcases(d).columns)),
                          y=prep_world_newcases(d).iloc[0],
                          name=prep_world_newcases(d).index[0]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_newcases(d).columns)),
                          y=prep_world_newcases(d).iloc[1],
                          name=prep_world_newcases(d).index[1]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_newcases(d).columns)),
                          y=prep_world_newcases(d).iloc[2],
                          name=prep_world_newcases(d).index[2]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_newcases(d).columns)),
                          y=prep_world_newcases(d).iloc[3],
                          name=prep_world_newcases(d).index[3]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_newcases(d).columns)),
                          y=prep_world_newcases(d).iloc[4],
                          name=prep_world_newcases(d).index[4]),
                        go.Bar(x=pd.to_datetime(np.array(prep_world_newcases(d).columns)),
                          y=prep_world_newcases(d).iloc[5],
                          name=prep_world_newcases(d).index[5]),
                        ]
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig

#County total cases
def make_fig_7_8(d1,d2, text):
  fig = go.Figure(go.Bar(y=prep_state_sum(d1,d2).sort_values(by=[text], ascending=True).index[-15:],
                          x=prep_state_sum(d1,d2).sort_values(by=[text],ascending=True)[text][-15:],
                         orientation='h'
                        )
                 )
  fig.update_layout(l_bar_s)
  return fig

#Region cululative cases

def make_fig_9(d):
  fig = go.Figure(data=[go.Bar(x=pd.to_datetime(np.array(prep_us_trend(d).columns)),
                          y=prep_us_trend(d).iloc[0],
                          name=prep_us_trend(d).index[0]),
                        go.Bar(x=pd.to_datetime(np.array(prep_us_trend(d).columns)),
                          y=prep_us_trend(d).iloc[1],
                          name=prep_us_trend(d).index[1]),
                        go.Bar(x=pd.to_datetime(np.array(prep_us_trend(d).columns)),
                          y=prep_us_trend(d).iloc[2],
                          name=prep_us_trend(d).index[2]),
                        go.Bar(x=pd.to_datetime(np.array(prep_us_trend(d).columns)),
                          y=prep_us_trend(d).iloc[3],
                          name=prep_us_trend(d).index[3])]
                                
                         #orientation='h'
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig

#New cases by region

def make_fig_10(d):
  fig = go.Figure(data=[go.Bar(x=pd.to_datetime(np.array(prep_us_newcases(d).columns)),
                          y=prep_us_newcases(d).iloc[0],
                          name=prep_us_newcases(d).index[0]),
                        go.Bar(x=pd.to_datetime(np.array(prep_us_newcases(d).columns)),
                          y=prep_us_newcases(d).iloc[1],
                          name=prep_us_newcases(d).index[1]),
                        go.Bar(x=pd.to_datetime(np.array(prep_us_newcases(d).columns)),
                          y=prep_us_newcases(d).iloc[2],
                          name=prep_us_newcases(d).index[2]),
                        go.Bar(x=pd.to_datetime(np.array(prep_us_newcases(d).columns)),
                          y=prep_us_newcases(d).iloc[3],
                          name=prep_us_newcases(d).index[3])]
                         #orientation='h'
                        )
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_s)
  return fig


#Worst hit local areas
def make_fig_12_13(d1,d2,d3,text):
  fig = go.Figure(go.Bar(y=prep_uk_scatter(d1,d2,d3).sort_values(by=[text], ascending=True).index[-15:],
                          x=prep_uk_scatter(d1,d2,d3).sort_values(by=[text],ascending=True)[text][-15:],
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


################################################
#### APP LAYOUT  ###############################
################################################


app.layout = html.Div([
## DIV BLOCK FOR HEADERS ETC
  html.Div([
    html.H5('Worldwide to date'),       
    html.P('Data Source: Johns Hopkins Univerity',style={'font-size': '1rem','color':'#696969'})
    ], 
    className='row flex-display', 
    style={'marginbottom':'15px','padding':'1%'},
    ),
  ##DIV BLOCK FOR GLOBAL CASES & Country graphs
  html.Div([
    html.Div([
      html.Div([
        html.Div([
          html.P('Cases:', 
            style={'color':'#696969', 'font-size': '1rem'}
            ),
          html.P('{}'.format(f'{df1[str(df1.columns[-1])].sum():,}'), 
            style={'font-size': '1.5rem'}
            )
          ],
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        html.Div([
          html.P('Deaths:', 
            style={'color':'#696969','font-size': '1rem'}
            ),
          html.P('{}'.format(f'{df2[str(df2.columns[-1])].sum():,}'), 
            style={'font-size': '1.5rem'}
            )
          ],
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        html.Div([
          html.P('Avg mortality:', 
            style={'color':'#696969','font-size': '1rem'}
            ),
          html.P('{} % '.format(round(100*df2[str(df2.columns[-1])].sum()/df1[str(df1.columns[-1])].sum(),2)), 
            style={'font-size': '1.5rem'}
            )
          ], 
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%','border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        ], 
        className='row flex-display', 
        ),
      html.Div([
        html.Div([
          html.Div([
            html.P('Statistics by country',
              style={'margin-bottom':'0', 'paddingBottom':'0','font-size': '1.5rem'}),
            html.P('Click for detail',
              style={'color':'#696969','font-size': '1rem', 'font-style':'italic'})
            ],
            className='eight columns'),
          html.Div([
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
          className='row'),
        dcc.Graph(id= "globe", config=conf)
        ],
        className='row flex-display',
        style={'padding':'1.5%'}
        ),
      ],
      className='seven columns flex-display',
      style={'marginbottom':'0%','paddingRight': '2%'},
      ),
    html.Div([
      html.Div([
        html.Div([
          html.P(id='world-cum-title',
              style={'margin':0,'font-size': '1.2rem'}),
          html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
          ], 
          className="eight columns"
          ),
        html.Div([
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
        className='row'),
      html.Div([
        dcc.Graph(id='world-trend-cum',config=conf,
          ),
        ],
        className='row',
        style={'marginbottom':'20%','paddingBottom': '5%'},
        ),
      html.Div([
        html.Div([
          html.Div([
            html.P(id='world-new-title',
                style={'margin':0,'font-size': '1.2rem'}),
            html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
            ], 
            className="eight columns"
            ),
          html.Div([
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
          className='row'),
        dcc.Graph(id='world-trend-new', config=conf,
          ),
        ],
        className='row',
        style={'marginbottom':'20%','paddingBottom': '5%'},
        ),
      html.Div([
        html.P("Worst hit countries",style={'font-size': '1.2rem'}, className='six columns'),
        html.Div([
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
              className="six columns"
              ),
        ],
        className='row'
        ),
      html.Div([
        html.Div([
          html.Div([
            html.P('Total',
                style={'font-size': '1rem'})
            ]),
          dcc.Graph(id='country-total',config=conf,)
          ],
          style={'marginbottom':'5%','paddingBottom': '5%'},
          className='six columns'
          ),
        html.Div([
          html.Div([
            html.P('per 100k pop.',
                style={'font-size': '1rem'})
            ]),
          dcc.Graph(id='country-capita',config=conf,)
          ],
          style={'marginbottom':'5%','paddingBottom': '5%'},
          className='six columns'),
          ],
        className='row',
        style={'marginbottom':'5%','paddingBottom': '5%'},
        ),    
      ], 
      className='five columns flex-display',
      style={'margin':'0%','padding': '0%'}
      ),
    ]),
##DIV BLOCK FOR HEATMAP AND COUNTRY TREND    
  html.Div([
    html.Div([
      html.Div([
        html.H6('Select countries for comparison', 
          style={'font-size': '1.5rem'}
          ),
        dcc.Dropdown(
          id='country-select',
          options = options,
          value = prep_countries_data(df1,df2).sort_values(by="Confirmed", ascending=False).index[:10],
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
      style={'padding':'1%', 'background-color':'#F5F5F5', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey', 'margin':'1%'}
      ),
    html.Div([
      html.Div([
        html.H6(id="line-header", 
          style = {'margin':0,'font-size':'1.5rem'}),
        html.P('Click on legend item to hide line', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
        dcc.RadioItems(
          id="uom",
          options=[
          {'label': 'Absolute', 'value': 'Abs'},
          {'label': 'per 100k pop.', 'value': 'per100k'}],
          value='per100k',
          labelStyle={'display': 'inline-block'},
          style={'font-size': '1rem'}),
        dcc.Graph(id="countries-conf",config=conf,style={'margin':'0%','padding': '2%'} 
          ),
        ], 
        className='six columns',style={'padding':'2%'}),
      html.Div([
        html.H6(id="heatmap-header", 
          style = {'font-size':'1.5rem'}),
        html.H6("incidences per 100k pop, 5d rolling average",
          style = {'font-size':'1rem'}),
        dcc.Graph(id='heatmap',config=conf, style={'margin':'0%','padding': '2%'})
        ], 
        className='six columns',style={'padding':'2%'}
        ),
      ],
      className='row flex-display',
      style={'padding':'1%'},
      )
    ]
    ),
  #BLOCK FOR US
  html.Div([
    html.H5('USA to date'),       
    html.P('Data Source: Johns Hopkins Univerity',style={'font-size': '1rem','color':'#696969'})
    ], 
    className='row', 
    style={'marginbottom':'15px','padding':'1%'},
    ),
    html.Div([
      html.Div([
          html.Div([
            html.Div([
                html.P('Cases:', 
                  style={'color':'#696969', 'font-size': '1rem'}
                  ),
                html.P('{}'.format(f'{prep_world_data(df1)[prep_world_data(df1).columns[-1]]["United States of America"]:,}'), 
                  style={'font-size': '1.5rem'}
                  )
                ],
                className='four columns',
                style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
                ),
            html.Div([
              html.P('Deaths:', 
                style={'color':'#696969','font-size': '1rem'}
                ),
              html.P('{}'.format(f'{prep_world_data(df2)[prep_world_data(df2).columns[-1]]["United States of America"]:,}'), 
                style={'font-size': '1.5rem'}
                )
              ],
              className='four columns',
              style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
              ),
            html.Div([
              html.P('Avg mortality:', 
                style={'color':'#696969','font-size': '1rem'}
                ),
              html.P('{} % '.format(round(100*prep_world_data(df2)[prep_world_data(df2).columns[-1]]["United States of America"]/prep_world_data(df1)[prep_world_data(df1).columns[-1]]["United States of America"],2)), 
                style={'font-size': '1.5rem'}
                )
              ],
              className='four columns',
              style={'background-color':'#F5F5F5','padding':'1%','border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
              ),
            ],
            className='row', 
            ),
          html.Div([
            html.Div([
              html.Div([
                html.P('Statistics by county',
                  style={'margin-bottom':'0', 'paddingBottom':'0','font-size': '1.5rem'}),
                html.P('Click for detail',
                  style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
                ],className='eight columns'),
              html.Div([
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
              className='row'),
            dcc.Graph(id= "US map",config=conf,)
            ],
            className='row flex-display',
            style={'padding':'1.5%'}
            ),
          ],
          className='seven columns flex-display',
          style={'margin':'0','paddingRight': '2%'},
          ),
      html.Div([
        html.Div([
          html.Div([
            html.Div([
              html.P(id='us-cum-title',
                  style={'margin':0,'font-size': '1.2rem'}),
              html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
              ], 
              className="eight columns"
              ),
            html.Div([
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
            className='row'),
          dcc.Graph(id='us-trend-total', config=conf,
            ),
          ],
          className='row',
          style={'marginbottom':'20%','paddingBottom': '5%'},
          ),
        html.Div([
          html.Div([
            html.Div([
              html.P(id='us-new-title',
                  style={'margin':0,'font-size': '1.2rem'}),
              html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
              ], 
              className="eight columns"
              ),
            html.Div([
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
          dcc.Graph(id='us-trend-new', config=conf,
            ),
          ],
          className='row',
          style={'marginbottom':'20%','paddingBottom': '5%'},
          ),
        html.Div([
          html.P("Worst hit states",style={'font-size': '1.2rem'}, className='six columns'),
          html.Div([
            dcc.RadioItems(
              id="top-states",
              options=[
              {'label':  'Cases', 'value': 'Cases'},
              {'label': 'Deaths', 'value': 'Deaths'}],
              value='Cases',
              labelStyle={'display': 'inline-block'},
              style={'font-size': '1rem','float':'right'},
            )
            ],
            className="six columns"
            ),
          ],
          className='row'
          ),
        html.Div([
          html.Div([
            html.Div([
              html.P('Total',
                  style={'font-size': '1rem'})
              ], 
              ),
            dcc.Graph(id='us-total',config=conf)
            ],
            style={'marginbottom':'5%','paddingBottom': '5%'},
            className='six columns'),
          html.Div([
            html.Div([
              html.P('per 100k pop.',
                  style={'font-size': '1rem'})
              ],
              ),
            dcc.Graph(id='us-capita',config=conf)
            ],
            style={'marginbottom':'5%','paddingBottom': '5%'},
            className='six columns'),
          ],
          className='row',
          style={'marginbottom':'5%','paddingBottom': '5%'},
          ) 
        ],
        className='five columns flex-display',
        style={'margin':'0%','padding': '0%'}
        ),
      ],
      className='row flex-display'
      ),
#BLOCK FOR UK
  html.Div([
    html.H5('Great Britain to date'),       
    html.P('Data Source: Public Health England, Public Health Wales, Scottish Government',style={'font-size': '1rem','color':'#696969'})
    ], 
    className='row', 
    style={'marginbottom':'15px','padding':'1%'},
    ),
    html.Div([
      html.Div([
          html.Div([
            html.Div([
                html.P('Cases:', 
                  style={'color':'#696969', 'font-size': '1rem'}
                  ),
                html.P('{}'.format(f'{prep_world_data(df1)[prep_world_data(df1).columns[-1]]["United Kingdom"]:,}'), 
                  style={'font-size': '1.5rem'}
                  )
                ],
                className='four columns',
                style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
                ),
            html.Div([
              html.P('Deaths:', 
                style={'color':'#696969','font-size': '1rem'}
                ),
              html.P('{}'.format(f'{prep_world_data(df2)[prep_world_data(df2).columns[-1]]["United Kingdom"]:,}'), 
                style={'font-size': '1.5rem'}
                )
              ],
              className='four columns',
              style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
              ),
            html.Div([
              html.P('Avg mortality:', 
                style={'color':'#696969','font-size': '1rem'}
                ),
              html.P('{} % '.format(round(100*prep_world_data(df2)[prep_world_data(df2).columns[-1]]["United Kingdom"]/prep_world_data(df1)[prep_world_data(df1).columns[-1]]["United Kingdom"],2)), 
                style={'font-size': '1.5rem'}
                )
              ], 
              className='four columns',
              style={'background-color':'#F5F5F5','padding':'1%','border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
              ),
            ],
            className='row', 
            ),
          html.Div([
            html.Div([
              html.Div([
                html.P('Statistics by nation',
                  style={'margin-bottom':'0', 'paddingBottom':'0','font-size': '1.5rem'}),
                html.P('Click for detail',
                  style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
                ],className='eight columns'),
              html.Div([
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
                )
              ], 
              className='row'),
            dcc.Graph(id= "UK map",config=conf,)
            ],
            className='row flex-display',
            style={'padding':'1.5%'}
            ),
          ],
          className='seven columns flex-display',
          style={'paddingBottom':'5%','paddingRight': '2%'},
          ),
      html.Div([
        html.Div([
          html.Div([
            html.Div([
              html.P(id='uk-cum-title',
                  style={'margin':0,'font-size': '1.2rem'}),
              html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
              ], 
              className="eight columns"
              ),
            html.Div([
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
              className="four columns"
              )
            ],
            className='row'),
          dcc.Graph(id='uk-trend-total',config=conf, 
            ),
          ],
          className='row',
          style={'marginbottom':'20%','paddingBottom': '5%'},
          ),
        html.Div([
          html.Div([
            html.Div([
              html.P(id='uk-new-title',
                  style={'margin':0,'font-size': '1.2rem'}),
              html.P('Click on legend item to zoom in', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
              ], 
              className="eight columns"
              ),
            html.Div([
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
              )
            ],
            className='row'),
          dcc.Graph(id='uk-trend-new',config=conf, 
            ),
          ],
          className='row',
          style={'marginbottom':'20%','paddingBottom': '5%'},
          ),
        html.Div([
          html.P("Worst hit local areas",style={'font-size': '1.2rem'})],
          className='row'
          ),
        html.Div([
          html.Div([
            html.Div([
              html.P('Total',
                  style={'font-size': '1rem'})
              ],
              ),
            dcc.Graph(id='uk-total', config=conf,figure=make_fig_12_13(england_cases, wales_cases, scot_cases,"Confirmed"))
            ],
            style={'marginbottom':'5%','paddingBottom': '5%'},
            className='six columns'),
          html.Div([
            html.Div([
              html.P('per 100k pop',
                  style={'font-size': '1rem'})
              ],
              ),
            dcc.Graph(id='uk-capita', config=conf,figure=make_fig_12_13(england_cases, wales_cases, scot_cases,"Conf100"))
            ],
            style={'marginbottom':'5%','paddingBottom': '5%'},
            className='six columns'),
          ],
          className='row',
          style={'marginbottom':'5%','paddingBottom': '5%'},
          ),
         
        ],
        className='five columns flex-display',
        style={'margin':'0%','padding': '0%'}
        ),
      ],
      className='row flex-display'
      )  
],
style={"display": "flex", "flex-direction": "column"}
)



################################################
#### APP CALLBACKS  ############################
################################################


#Callback for world map UoM
@app.callback(
  Output('globe', 'figure'),
  [Input('uom-ww-map', 'value')])
def update_chart(units):
  if units == 'per100k':
    d = go.Figure(go.Scattergeo(
    lon=prep_countries_data(df1,df2)["longitude"],
    lat=prep_countries_data(df1,df2)["latitude"],
    text = prep_countries_data(df1,df2)['text100'],
    hoverinfo = 'text',
    marker=dict(
        size= 0.5*prep_countries_data(df1,df2)["Conf100"],
        line_width=0.5,
        sizemode='area'
    )))
  else:
    d=go.Scattergeo(
    lon=prep_countries_data(df1,df2)["longitude"],
    lat=prep_countries_data(df1,df2)["latitude"],
    text = prep_countries_data(df1,df2)['text'],
    hoverinfo = 'text',
    marker=dict(
        size= 0.003*prep_countries_data(df1,df2)["Confirmed"],
        line_width=0.5,
        sizemode='area'
    )
)

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
    return make_fig_4(df1)
  else:
    return make_fig_4(df2)

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
    return make_fig_5(df1)
  else:
    return make_fig_5(df2)

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
    return make_fig_2_3(df1,df2,"Confirmed")
  else:
    return make_fig_2_3(df1,df2,"Deaths")

@app.callback(
  Output('country-capita', 'figure'),
  [Input('top-countries', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_2_3(df1,df2,"Conf100")
  else:
    return make_fig_2_3(df1,df2,"Deaths100")

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
      if uom =="Abs":
          d3=[{
          'x': pd.to_datetime(np.array(prep_world_data(df1).columns)),
          'y': prep_world_data(df1)[prep_world_data(df1).index==country].values[0],
          'name': country
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
          #fig3.update_layout(yaxis_type="log")
      else:
          d3=[{
          'x': pd.to_datetime(np.array(prep_world_data(df1).columns)),
          'y': prep_world_capita(df1).loc[:, :df1.columns[-1]][prep_world_capita(df1).index==country].values[0],
          'name': country
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
    else:
      if uom =="Abs":
            d3=[{
            'x': pd.to_datetime(np.array(prep_world_data(df2).columns)),
            'y': prep_world_data(df2)[prep_world_data(df2).index==country].values[0],
            'name': country
            } for country in li]
            fig3=go.Figure(data=d3,layout=l_trend)
            #fig3.update_layout(yaxis_type="log")
      else:
          d3=[{
          'x': pd.to_datetime(np.array(prep_world_data(df2).columns)),
          'y': prep_world_capita(df2).loc[:, :df2.columns[-1]][prep_world_capita(df2).index==country].values[0],
          'name': country
          } for country in li]
          fig3=go.Figure(data=d3,layout=l_trend)
    return fig3

#Callbacks for heatmap
@app.callback(
  Output('heatmap-header','children'),
  [Input('trend', 'value')])

def update_header(trend):
  if trend=="Cases":
    return "Infection Rate"
  else:
    return "Death Rate"

@app.callback(
    Output('heatmap', 'figure'),
    [Input('country-select', 'value'),
    Input('trend', 'value')])
def update_chart(selection, trend):
    li=[]
    for c in selection:
        li.append(c)
    if trend == "Deaths":
        data=go.Heatmap(
        z=prep_rolling_avg(df2).loc[li],
        x=pd.to_datetime(np.array(prep_rolling_avg(df2).columns)),
        y=li,
        colorscale='Blues',
        colorbar={"thickness":10, "tickfont":{"size":10}},
        )
        fig4=go.Figure(data=data,layout=l_trend)
    else:
        data=go.Heatmap(
        z=prep_rolling_avg(df1).loc[li],
        x=pd.to_datetime(np.array(prep_rolling_avg(df1).columns)),
        y=li,
        colorscale='Blues',
        colorbar={"thickness":10, "tickfont":{"size":10}},
        )
        fig4=go.Figure(data=data,layout=l_trend)
    return fig4

#Callback for US map UoM
@app.callback(
  Output('US map', 'figure'),
  [Input('uom-us-map', 'value')])
def update_chart(units):
  if units=='per100k':
    d=go.Scattergeo(
    lon = prep_county_sum(df3,df4)['Long_'],
    lat = prep_county_sum(df3,df4)['Lat'],
    text = prep_county_sum(df3,df4)['text100'],
    hoverinfo = 'text',
    marker = dict(
            size = 0.1*prep_county_sum(df3,df4)['Conf100'],
            line_width=0.5,
            sizemode = 'area'
        ))
  else:
    d= go.Scattergeo(
        lon = prep_county_sum(df3,df4)['Long_'],
        lat = prep_county_sum(df3,df4)['Lat'],
        text = prep_county_sum(df3,df4)['text'],
        hoverinfo = 'text',
        marker = dict(
                size = 0.05*(prep_county_sum(df3,df4)['Confirmed']),
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
    return make_fig_9(df3)
  else:
    return make_fig_9(df4)

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
    return make_fig_10(df3)
  else:
    return make_fig_10(df4)

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
    return make_fig_7_8(df3,df4,"Confirmed")
  else:
    return make_fig_7_8(df3,df4,"Deaths")

@app.callback(
  Output('us-capita', 'figure'),
  [Input('top-states', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_7_8(df3,df4,"Conf100")
  else:
    return make_fig_7_8(df3,df4,"Deaths100")

#Callback for UK map UoM
@app.callback(
  Output('UK map', 'figure'),
  [Input('uom-uk-map', 'value')])
def update_chart(units):
  if units == "Abs":
    d=go.Scattermapbox(
    lon = prep_uk_scatter(england_cases, wales_cases, scot_cases)['long'],
    lat = prep_uk_scatter(england_cases, wales_cases, scot_cases)['lat'],
    text = prep_uk_scatter(england_cases, wales_cases, scot_cases)['text'],
    hoverinfo = 'text',
    marker = dict(
            size = 0.05*prep_uk_scatter(england_cases, wales_cases, scot_cases)['Confirmed'],
            #line_width=0.5,
            sizemode = 'area',
        symbol = 'circle'
        ))
  else:
    d=go.Scattermapbox(
    lon = prep_uk_scatter(england_cases, wales_cases, scot_cases)['long'],
    lat = prep_uk_scatter(england_cases, wales_cases, scot_cases)['lat'],
    text = prep_uk_scatter(england_cases, wales_cases, scot_cases)['text100'],
    hoverinfo = 'text',
    marker = dict(
            size = 0.2*prep_uk_scatter(england_cases, wales_cases, scot_cases)['Conf100'],
            #line_width=0.5,
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
    fig = go.Figure(data=go.Bar(x=pd.to_datetime(prep_world_data(df2).columns),
                            y=prep_world_data(df2)[prep_world_data(df2).index=="United Kingdom"].values[0]),
                          )
    fig.update_layout(barmode='stack')
    fig.update_layout(l_bar_s)
    return fig

@app.callback(
  Output('uk-cum-title', 'children'),
  [Input('uk-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "Cumulative cases"
  else:
    return "Cumulative deaths"

@app.callback(
  Output('uk-trend-new', 'figure'),
  [Input('uk-new', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return make_fig_15(eng_trend, wales_trend, scot_trend)
  else:
    fig = go.Figure(data=go.Bar(x=pd.to_datetime(prep_world_data(df2).columns[:-1]),
                          y=prep_world_data(df2)[prep_world_data(df2).index=="United Kingdom"].values[0][1:]-prep_world_data(df2)[prep_world_data(df2).index=="United Kingdom"].values[0][:-1]),
                        )
    fig.update_layout(barmode='stack')
    fig.update_layout(l_bar_s)
    return fig

@app.callback(
  Output('uk-new-title', 'children'),
  [Input('uk-new', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "New cases"
  else:
    return "New deaths"


if __name__ == '__main__':
	app.run_server()
