import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from requests import get
from json import dumps
import datetime

from app import app

text_color_main="white"
text_color_sub="#D3D3D3"
main_color= "#181818"
background_color = "#181818"
country_border = "#808080"

################################################
#### DATA FOR UK ANALYSES ######################
################################################

url_1='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_2='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
df1=pd.read_csv(url_1)
df2=pd.read_csv(url_2)

uk_pop=pd.read_csv("data/uk_pop.csv").rename(columns={"Name": "name"})
uk_map=pd.read_csv("data/uk_mapp.csv")
#uk_map=uk_map.append({"code":"N92000002","name":"Northern Ireland","long":-6.4923,"lat":54.7877}, ignore_index=True)
#uk_map=uk_map.append({"code":"S92000003","name": "Scotland","long":-4.2026,"lat":56.4907}, ignore_index=True)
#uk_map=uk_map.append({"code":"W92000004","name": "Wales","long":-3.7837,"lat":52.1307}, ignore_index=True)
full_ltla=pd.read_csv("data/full_ltla.csv")
full_region=pd.read_csv("data/full_region.csv")
full_nation=pd.read_csv("data/full_nation.csv")
newcase_ltla=pd.read_csv("data/newcase_ltla.csv")

def get_hist_data(date, areaType):
    ENDPOINT = "https://api.coronavirus.data.gov.uk/v1/data"
    AREA_TYPE = areaType
    DATE = date
    
    if areaType=="nation":
        dailyCases="newCasesByPublishDate"
        cumulativeCases="cumCasesByPublishDate"
        dailyDeaths="newDeaths28DaysByPublishDate"
        cumulativeDeaths="cumDeaths28DaysByPublishDate"
    else:
        dailyCases="newCasesBySpecimenDate"
        cumulativeCases="cumCasesBySpecimenDate"
        dailyDeaths="newDeaths28DaysByDeathDate"
        cumulativeDeaths="cumDeaths28DaysByDeathDate"

    structure = {
        "date": "date",
        "name": "areaName",
        "areaType": "areaType",
        "code": "areaCode",
        "dailyCases": dailyCases,
        "cumulativeCases": cumulativeCases,
        "dailyDeaths": dailyDeaths,
        "cumulativeDeaths": cumulativeDeaths
    }

    filters = [
        f"areaType={ AREA_TYPE }",
        f"date={ DATE }"
    ]
    api_params = {
        "filters": str.join(";", filters),
        "structure": dumps(structure, separators=(",", ":")),
    }

    api_params["format"] = "csv"
    fmt="csv"
    response = get(ENDPOINT, params=api_params, timeout=10)
    assert response.status_code == 200, f"Failed request for {fmt}: {response.text}"
    f = open('newfile.csv', "w")
    f.write(response.text)
    f.close()
    return pd.read_csv("newfile.csv")

def get_data(geo_type, geo, scope):
    ENDPOINT = "https://api.coronavirus.data.gov.uk/v1/data"
    AREA_TYPE = geo_type
    AREA_NAME = geo
    
    
    if AREA_TYPE == "nation":
        dailyCases="newCasesBySpecimenDate"
        cumulativeCases="cumCasesBySpecimenDate"
        dailyDeaths="newDeaths28DaysByDeathDate"
        cumulativeDeaths="cumDeaths28DaysByDeathDate"
    else:
        dailyCases="newCasesByPublishDate"
        cumulativeCases="cumCasesByPublishDate"
        dailyDeaths="newDeaths28DaysByPublishDate"
        cumulativeDeaths="cumDeaths28DaysByPublishDate"
    
    latest_by=cumulativeCases
    
    structure = {
        "date": "date",
        "name": "areaName",
        "areaType": "areaType",
        "code": "areaCode",
        "dailyCases": dailyCases,
        "cumulativeCases": cumulativeCases,
        "dailyDeaths": dailyDeaths,
        "cumulativeDeaths": cumulativeDeaths  
    }
    
    if scope=="all":
        if geo=="":
            filters = [
                f"areaType={ AREA_TYPE }",
            ]
            api_params = {
                "filters": str.join(";", filters),
                "structure": dumps(structure, separators=(",", ":")),
            }
        else:
            filters = [
                f"areaType={ AREA_TYPE }",
                f"areaName={ AREA_NAME }"
            ]
            api_params = {
                "filters": str.join(";", filters),
                "structure": dumps(structure, separators=(",", ":")),
            }
    else:
        if geo=="":
            filters = [
                f"areaType={ AREA_TYPE }",
            ]
            api_params = {
                "filters": str.join(";", filters),
                "structure": dumps(structure, separators=(",", ":")),
                "latestBy": latest_by
            }
        else:
            filters = [
                f"areaType={ AREA_TYPE }",
                f"areaName={ AREA_NAME }"
            ]
            api_params = {
                "filters": str.join(";", filters),
                "structure": dumps(structure, separators=(",", ":")),
                "latestBy": latest_by
            }

    api_params["format"] = "csv"
    response = get(ENDPOINT, params=api_params, timeout=10)
    f = open('newfile.csv', "w")
    f.write(response.text)
    f.close()
    return pd.read_csv("newfile.csv")

#REFRESH DATA
try:
    full_nation=get_data("nation","","all")
    full_nation=full_nation.drop_duplicates()
    full_nation.to_csv("data/full_nation.csv", index=False)
except:
    pass

try:
    full_region=get_hist_data(str(datetime.date.today()-datetime.timedelta(days=2)), "region").append(full_region, ignore_index=True)
    full_region=full_region.drop_duplicates(subset=["code", "date"], keep="first")
    full_region.to_csv("data/full_region.csv", index=False)
except:
    pass

try:
    full_ltla=get_hist_data(str(datetime.date.today()-datetime.timedelta(days=1)), "ltla").append(full_ltla, ignore_index=True)
    full_ltla=get_hist_data(str(datetime.date.today()-datetime.timedelta(days=3)), "ltla").append(full_ltla, ignore_index=True)
    full_ltla=get_hist_data(str(datetime.date.today()-datetime.timedelta(days=2)), "ltla").append(full_ltla, ignore_index=True)
    full_ltla=full_ltla.drop_duplicates(subset=["code", "date"], keep="first")
    full_ltla.to_csv("data/full_ltla.csv", index=False)
except:
    pass

try:
    url = "https://www.opendata.nhs.scot/dataset/b318bddf-a4dc-4262-971f-0ba329e09b87/resource/427f9a25-db22-4014-a3bc-893b68243055/download/trend_ca_20200906.csv"
    scot_data = pd.read_csv(url)

    date2=[]
    for i in scot_data["Date"]:
        date2.append(str(i)[:4]+"-"+str(i)[4:6]+"-"+str(i)[6:])

    to_add=pd.DataFrame({"date":date2, 
                         "areaType":"ltla", 
                         "code":list(scot_data["CA"]), 
                         "dailyCases":list(scot_data["DailyPositive"]), 
                         "cumulativeCases":list(scot_data["CumulativePositive"]), 
                         "dailyDeaths":list(scot_data["DailyDeaths"]), 
                         "cumulativeDeaths":list(scot_data["CumulativeDeaths"])
                        })

    b=to_add.merge(full_ltla[["code", "name"]].drop_duplicates(), how = "left")

    full_ltla=b.append(full_ltla).drop_duplicates(subset=["code", "date"], keep="first")

    full_ltla.to_csv("data/full_ltla.csv", index=False)
except:
  pass

def newcase_avg(df, d):
    b=pd.DataFrame()
    names=[]
    codes=[]
    rollingAvg=[]
    df=df.drop(df[df["name"].isna()].index)
    for i in set(df["name"]):
        a=df[df["name"]==i].sort_values(by="date")
        names.append(i)
        codes.append(df["code"][df["name"]==i].iloc[0])
        rollingAvg.append(a.drop(a[a["cumulativeCases"].isna()].index).tail(d)["dailyCases"].mean())
    b["name"]=names
    b["code"]=codes
    b["rollingAvg"]=rollingAvg
    return b

newcase_avg(full_ltla, 7).to_csv("data/newcase_ltla.csv", index=False)

def prep_scat_cum():
    a=full_ltla.drop(full_ltla[full_ltla["cumulativeCases"].isna()].index)
    a=a.groupby("name").max()
    a["name"]=a.index
    a=a.merge(uk_map[["code", "long", "lat"]])
    return a



################################################
#### CHART LAYOUTS #############################
################################################

#WORLD & US MAPS
l_map=go.Layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    height=375,
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
  height=270,
  template="plotly_dark",
  paper_bgcolor = main_color,
  plot_bgcolor = main_color,
  #width=90,
  margin={"r":5,"t":0,"l":0,"b":0},
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

#############################################
############ CHARTS #########################
#############################################

def build_scatter_cum(metric):
    uk_scat=prep_scat_cum()
    uk_scat["text"]= '<b>'+uk_scat["name"]+'</b>'+ '<br>Cumulative cases: ' + '<br>'+(round(uk_scat[metric],0)).astype(int).astype(str)
    d=go.Scattergeo(
    lon = uk_scat['long'],
    lat = uk_scat['lat'],
    text = uk_scat["text"],
    hoverinfo = 'text',
    marker = dict(
            size = 0.02*np.clip(round(uk_scat[metric]),a_min=0, a_max=None),
            sizemode = 'area',
        symbol = 'circle'
        ))
    fig11=go.Figure(data=d)
    fig11.update_layout(l_map)
    fig11.update_geos(scope="europe",lataxis_showgrid=False, lonaxis_showgrid=False,lataxis_range=[50.8,58.5],lonaxis_range=[-11,2])
    return fig11

def build_scatter_new(metric):
    g=newcase_ltla.fillna(0)
    g=g.merge(uk_map[["code", "long", "lat"]], how="left")
    g["text"]= '<b>'+g["name"]+'</b>'+'<br>New cases per day: ' + '<br>'+(round(g[metric])).astype(int).astype(str)
    d=go.Scattergeo(
    lon = g['long'],
    lat = g['lat'],
    text = g["text"],
    hoverinfo = 'text',
    marker = dict(
            size = 1*np.clip(round(g[metric]),a_min=0, a_max=None),
            sizemode = 'area',
        symbol = 'circle'
        ))
    fig11=go.Figure(data=d)
    fig11.update_layout(l_map)
    fig11.update_geos(scope="europe",lataxis_showgrid=False, lonaxis_showgrid=False, lataxis_range=[50.8,58.5],lonaxis_range=[-11,2])
    return fig11

def make_trend(metric):
    trend=full_nation
    fig = go.Figure(data=[go.Bar(x=trend["date"][trend["name"]=="England"],
                          y=trend[metric][trend["name"]=="England"],
                          name="England"),
                        go.Bar(x=trend["date"][trend["name"]=="Wales"],
                          y=trend[metric][trend["name"]=="Wales"],
                          name="Wales"),
                        go.Bar(x=trend["date"][trend["name"]=="Scotland"],
                          y=trend[metric][trend["name"]=="Scotland"],
                          name="Scotland"),
                        go.Bar(x=trend["date"][trend["name"]=="Northern Ireland"],
                          y=trend[metric][trend["name"]=="Northern Ireland"],
                          name="N. Ireland"), 
                         ]
                        )
    fig.update_layout(barmode='stack')
    fig.update_layout(l_bar_w)
    return fig

def make_fig_comp(metric, areaType):
    if areaType=="region":
        dat=full_region.append(full_nation[full_nation["name"]!="England"]).groupby("code").max()
    else:
        dat=full_ltla.groupby("code").max().fillna(0)
    if areaType=="ltla":
        fig = go.Figure(go.Bar(y=dat.sort_values(by=[metric], ascending=True)["name"][-15:],
                              x=dat.sort_values(by=[metric],ascending=True)[metric][-15:],
                             orientation='h'
                            )
                     )
    else:
        fig = go.Figure(go.Bar(y=dat.sort_values(by=[metric], ascending=True)["name"],
                              x=dat.sort_values(by=[metric],ascending=True)[metric],
                             orientation='h'
                            )
                     )
    fig.update_layout(l_bar_s)
    return fig

def make_fig_comp_2(metric, areaType):
    if areaType=="region":
        g=newcase_avg(full_region,7).append(newcase_avg(full_nation,7)[newcase_avg(full_nation,7)["name"]!="England"]).fillna(0)
    else:
        g=newcase_ltla.fillna(0)
    #g=g.merge(uk_pop[["code","All ages"]], how="left", left_index=True, right_on="code")
    #g["dailyCases100"]=g["dailyCases"]*100000/g["All ages"]
    if areaType=="ltla":
        fig = go.Figure(go.Bar(y=[i.title() for i in g.sort_values(by=[metric], ascending=True)["name"]][-15:],
                              x=g.sort_values(by=[metric],ascending=True)[metric][-15:].round(0),
                             orientation='h'
                            )
                     )
    else:
        fig = go.Figure(go.Bar(y=[i.title() for i in g.sort_values(by=[metric], ascending=True)["name"]],
                              x=g.sort_values(by=[metric],ascending=True)[metric].round(2),
                             orientation='h'
                            )
                     )
    fig.update_layout(l_bar_s)
    return fig

def make_time_series_uk(area, metric):
    dat=full_ltla[full_ltla["name"]==area].fillna(0)
    fig = go.Figure(data=go.Bar(x=pd.to_datetime(np.array(dat["date"])),
                          y=dat[metric],
                        ))
    fig.update_layout(l_bar_w)
    return fig


areas = [{'label':"United Kingdom", 'value':"United Kingdom"}]
for tic in list(full_ltla["name"].drop_duplicates().sort_values()):
  areas.append({'label':tic, 'value':tic})

##########################################
########  STYLES  ########################
##########################################

section_header = {'color':text_color_main, 'font-size': '1.5rem','background-color': "#181818", "margin-bottom":0}
section_subheader = {'font-size': '1.3rem', 'color': text_color_main,  'background-color': "#181818", 'margin-bottom':'1%'}
main_columns = {'paddingRight':'0%','paddingLeft':'0%'}
section_wrapper = {"padding": "2%"}
col_fill = {"background-color": "#181818"}

##########################################
############# LAYOUT #####################
##########################################

layout = html.Div([
  html.Div([#row for UK header
    html.H5('United Kingdom as of {}'.format(pd.to_datetime(df1.columns[-1]).strftime('%B %d, %Y')), 
      style={"margin-bottom":0, 'color':text_color_main}),            
    html.P('Data source: UK Government, Scottish Government. Note: Daily data per nation is collected by the devolved administrations via separate processes and timelines.',
      style={'font-size': '1rem','color':text_color_sub, "margin-bottom":0,})
    ], 
    className='row subtitle', 
    style={'marginbottom':'15px','paddingTop':'1%','paddingBottom':'1%'},
    ),
  html.Div([#row for title tiles
    html.Div([#cases
      html.P('Cases:', 
        style={'color':text_color_main, 'font-size': '1.5rem', 'margin-bottom':'0%'}
        ),
      html.P('{}'.format(f'{int(df1[df1.columns[-1]][df1["Country/Region"]=="United Kingdom"].sum()):,}'), 
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
      html.P('{}'.format(f'{int(df2[df2.columns[-1]][df2["Country/Region"]=="United Kingdom"].sum()):,}'), 
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
      html.P('{} % '.format(round(100*df2[df2.columns[-1]][df2["Country/Region"]=="United Kingdom"].sum()/df1[df1.columns[-1]][df1["Country/Region"]=="United Kingdom"].sum(),1)), 
        style={'color':'#FF8C00','font-size': '3rem','font-weight': 'bold','margin-bottom':'3%'}
        )
      ], 
      className='four columns',
      style={'text-align': 'center'}
      ),
    ],
    className='row',
    ),
  html.Div([#row for UK body
    html.Div([#four columns for LHS
      html.Div([#row for map
        html.Div([ #row for titles
          html.Div([# title
            html.H6('Spread by location', 
              style = section_header
              ),
            ],
            ),
          html.Div([#radio items
            dcc.RadioItems(
              id="uom-uk-map",
              options=[
              {'label': 'Daily', 'value': 'newcases'},
              {'label': 'Cumulative', 'value': 'cumcases'},  
              ],
              value='newcases',
              labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
              ),
            ],
            style = section_subheader
            ),
          ],
          className = 'row subtitle'
          ),      
        html.Div([# row for map itself
          dcc.Loading(
            dcc.Graph(id= "UK map",
              #figure=build_scatter_new("rollingAvg"), 
              config=conf
              ),
            ),
          html.P("Note: Daily numbers are the average of the most recent 7 days' data",
            style={'font-size': '1rem','color':text_color_sub, 'margin-bottom':0, 'paddingLeft':'1%'})
          ],
          style = col_fill
          ),
        ],
        className='row',
        style={'margin-bottom': "2%"}
        ),
      html.Div([#row for bar charts
        html.Div([#row for titles
            html.Div([#eight columns for text
              html.H6("Worst-hit areas",
                style=section_header
                ),
              ],
              ),
            html.Div([
              dcc.RadioItems(
                id="top-areas",
                options=[
                {'label': 'Daily', 'value': 'new'},
                {'label':  'Cumulative', 'value': 'cum'}
                ],
                value='new',
                labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
              )
              ],
              style=section_subheader 
              )
            ],
            className='row subtitle'
            ),
        html.Div([#row for charts
          html.Div([#six columns for total
            html.P('By local authority',
              style=section_subheader
              ),
            dcc.Loading(
              dcc.Graph(id="ltla-rank", 
              #figure=make_fig_comp_2("rollingAvg","ltla"),
              config=conf
              ),
              ),
            ], 
            className="six columns",
            style = section_wrapper
            ),
          html.Div([#six columns for per 100k
            html.P('By region',
              style=section_subheader
              ),
            dcc.Loading(
              dcc.Graph(id='region-rank', 
              #figure=make_fig_comp_2("rollingAvg","region"),
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
          style = section_subheader
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
          html.H6('Trend by UK Local Authority',
            style = section_header,
            ),
          ],
          ),
        html.Div([#four columns for radio items
          dcc.RadioItems(
            id='uk-cum',
            options=[
            {'label':  'Cases', 'value': 'Cases'},
            {'label': 'Deaths', 'value': 'Deaths', 'disabled': False}
            ],
            value='Cases',
            labelStyle={'display': 'inline-block', 'margin':'0', 'margin-right': '1%','font-weight': 'normal'},
          )
          ],
          className="row",
          style=section_subheader
          ),
        html.Div([#row for dropdown
          dcc.Dropdown(
            id="UK-selector",
            options=areas,
            value ='United Kingdom',
            multi = False,
            ),
          ], 
          className="row",
          style = {'color': text_color_main,  'background-color': main_color, 'margin-bottom':0, 'margin-top':'1%','padding': '0%'}
          ),
        html.P("Note: Due to lack of complete data, deaths by Local Authority are not shown.",
          style={'font-size': '1rem','color':text_color_sub, 'margin-bottom':0, 'paddingTop':'1%'}) 
        ],
        className = 'row subtitle'
        ),
      html.Div([ #wrapper
        html.Div([#row for new cases
          html.Div([#row for titles
            html.Div([#eight columns for text
              html.P(id='uk-new-title', children= "New cases",
                style=section_subheader
                ),
              ], 
              ),     
            ],
            className='row',
            ),
          html.Div([#row for new cases dcc chart
            dcc.Loading(
              dcc.Graph(id='uk-trend-new',
              #figure=make_trend("dailyCases"), 
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
          html.Div([#row for titles
            html.Div([#eight columns for text
              html.P(id='uk-cum-title', children= "Cumulative cases",
                style=section_subheader
                ),
              ], 
              ),
            ],
            className='row'
            ),
          html.Div([#row for dcc cum chart
            dcc.Loading(
              dcc.Graph(id='uk-trend-total',
              #figure=make_trend("cumulativeCases"), 
              config=conf 
              )
              ),
            ],
            className='row'
            ),
          ], 
          className='row',
          style=section_wrapper
          ), 
        ], 
        style = col_fill)
      ],
      className='six columns',
      ),
    ],
    className='row'
    ),
],
style={"padding": "0%"}
)


#CALLBACKS
#Callback for UK map UoM
@app.callback(
  Output('UK map', 'figure'),
  [Input('uom-uk-map', 'value')])
def update_chart(value):
  if value == "newcases":
    fig = build_scatter_new("rollingAvg")
  elif value == "cumcases":
    fig = build_scatter_cum("cumulativeCases")
  return fig

#Callbacks for RHS UK charts
@app.callback(
  Output('ltla-rank', 'figure'),
  [Input('top-areas', 'value'),
  ])

def update_chart(metric):
  if metric == "cum":
    return make_fig_comp("cumulativeCases", "ltla")
  else:
    return make_fig_comp_2("rollingAvg","ltla")

#Callbacks for RHS UK charts
@app.callback(
  Output('region-rank', 'figure'),
  [Input('top-areas', 'value'),
  ])

def update_chart(metric):
  if metric == "cum":
    return make_fig_comp("cumulativeCases", "region")
  else:
    return make_fig_comp_2("rollingAvg","region")

#Callbacks for RHS UK charts

@app.callback(
  [Output('uk-cum', 'options'),
  Output('uk-cum', 'value')], 
  [Input('UK-selector', 'value')])
def update_item(scope):
  if scope == "United Kingdom":
    options = [{'label':  'Cases', 'value': 'Cases'},{'label': 'Deaths', 'value': 'Deaths', 'disabled': False}]
    value = 'Cases'
    return options, value
  else:
    options = [{'label':  'Cases', 'value': 'Cases'},{'label': 'Deaths', 'value': 'Deaths', 'disabled': True}]
    value = 'Cases'
    return options, value

@app.callback(
  Output('uk-trend-total', 'figure'),
  [Input('UK-selector', 'value'),
  Input("uk-cum", "value")
  ])
def update_chart(scope,metric):
  if scope == "United Kingdom":
    if metric == "Cases":
      return make_trend("cumulativeCases")
    else:
      return make_trend("cumulativeDeaths")
  else:
    return make_time_series_uk(scope, "cumulativeCases")

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
  [Input('UK-selector', 'value'),
  Input("uk-cum", "value")
  ])
def update_chart(scope,metric):
  if scope == "United Kingdom":
    if metric == "Cases":
       return make_trend("dailyCases")
    else:
      return make_trend("dailyDeaths")
  else:
    return make_time_series_uk(scope, "dailyCases")

@app.callback(
  Output('uk-new-title', 'children'),
  [Input('uk-cum', 'value')])

def update_chart(trend):
  if trend == 'Cases':
    return "New cases"
  else:
    return "New deaths"


