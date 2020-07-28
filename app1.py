import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests
import io


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#external_stylesheets = ['https://codepen.io/mainaminor/pen/wvaOEmY.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, 
  meta_tags=[{"name": "viewport", "content": "width=device-width"}]
  )

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>COVID-19 Global Spread</title>
        <meta property="og:title" content="Global spread of the novel coronavirus">
        <meta property="og:image" content="assets/covid_dash.png">
        <meta name="description" property="og:description" content="An interactive mini-dashboard built and deployed by me in Python, giving a summary of coronavirus spread, with deep dives for the United States and United Kingdom.">
        <meta name="author" content="Anthony S N Maina">
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

server = app.server

################################################
#### DATA FOR WORLDWIDE ANALYSES ###############
################################################

continents=pd.read_csv("data/continents.csv").drop(columns="Unnamed: 0")
df_p=pd.read_csv("data/worldpop.csv").set_index("Location")
ctrs=pd.read_csv('data/countries.csv').set_index("name")

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

def prep_country_newcases(d):
    df=prep_world_data(d)
    country_newcases=pd.DataFrame(index=df.index,columns=list(df.columns[1:]))
    for i in range(len(df.columns)-1):
        f=df[df.columns[i+1]]-df[df.columns[i]]
        country_newcases[country_newcases.columns[i]]=f
    return country_newcases

##HEATMAP##

def prep_rolling_avg (d):
    d1=prep_world_data(d)
    sr_7d=pd.DataFrame(index=d1.index,columns=list(d1.columns[7:]))
    for i in range(len(d1.columns)-7):
        f=(d1[d1.columns[i+7]]-d1[d1.columns[i]])/7
        sr_7d[sr_7d.columns[i]]=f
    return sr_7d
    

def prep_world_capita (d):
    d1=prep_world_data(d)
    t=d1.merge(df_p, left_index=True, right_index=True)
    a=t.loc[:, :d1.columns[-1]].values.transpose()
    b=100/t["PopTotal"].values
    c=a*b
    t.loc[:, :d1.columns[-1]]=c.transpose()
    return t

def prep_rolling_capita(d):
    d1=prep_world_capita(d)
    d11=prep_world_data(d)
    sr_7d=pd.DataFrame(index=d1.index,columns=list(d11.columns[7:]))
    for i in range(len(d11.columns)-7):
        f=(d1[d1.columns[i+7]]-d1[d1.columns[i]])/7
        sr_7d[sr_7d.columns[i]]=f
    return sr_7d

##################################################


try:
  countries_data= prep_countries_data(df1, df2)
  world_data_cases= prep_world_data(df1)
  world_data_deaths= prep_world_data(df2)
  world_trend_cases= prep_world_trend(df1)
  world_trend_deaths= prep_world_trend(df2)
  world_newcases_cases= prep_world_newcases(df1)
  world_newcases_deaths= prep_world_newcases(df2)
  world_capita_cases= prep_world_capita(df1)
  world_capita_deaths= prep_world_capita(df2)
  rolling_avg_cases= prep_rolling_avg(df1)
  rolling_avg_deaths= prep_rolling_avg(df2)
  rolling_capita_cases= prep_rolling_capita(df1)
  rolling_capita_deaths= prep_rolling_capita(df2)
  country_newcases_cases= prep_country_newcases(df1)
  country_newcases_deaths= prep_country_newcases(df2)
  countries_data.to_csv("data/countries_data.csv")
  world_data_cases.to_csv("data/world_data_cases.csv")
  world_data_deaths.to_csv("data/world_data_deaths.csv")
  world_trend_cases.to_csv("data/world_trend_cases.csv")
  world_trend_deaths.to_csv("data/world_trend_deaths.csv")
  world_newcases_cases.to_csv("data/world_newcases_cases.csv")
  world_newcases_deaths.to_csv("data/world_newcases_deaths.csv")
  world_capita_cases.to_csv("data/world_capita_cases.csv")
  world_capita_deaths.to_csv("data/world_capita_deaths.csv")
  rolling_avg_cases.to_csv("data/rolling_avg_cases.csv")
  rolling_avg_deaths.to_csv("data/rolling_avg_deaths.csv")
  rolling_capita_cases.to_csv("data/rolling_capita_cases.csv")
  rolling_avg_deaths.to_csv("data/rolling_capita_deaths.csv")
  country_newcases_cases.to_csv("data/country_newcases_cases.csv")
  country_newcases_deaths.to_csv("data/country_newcases_deaths.csv")
except:
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
  countries_newcases_cases=pd.read_csv("data/countries_newcases_cases.csv").set_index("Unnamed: 0")
  countries_newcases_deaths=pd.read_csv("data/countries_newcases_deaths.csv").set_index("Unnamed: 0")



options = []
for tic in world_data_cases.index:
  options.append({'label':tic, 'value':tic})

li2=list(countries_data[countries_data["PopTotal"]>5000].sample(100, replace=True, random_state=9).index)  



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

def prep_state_data(d):
    df=d.groupby(by="Province_State").sum()
    df.rename(index={"District of Columbia": "D.C."}, inplace=True)
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
    df.rename(index={"District of Columbia": "D.C."}, inplace=True)
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

def prep_state_newcases(d):
    df=prep_state_data(d)
    dff=pd.DataFrame(index=df.index,columns=list(df.columns[1:]))
    for i in range(len(df.columns)-1):
        f=df[df.columns[i+1]]-df[df.columns[i]]
        dff[dff.columns[i]]=f
    return dff

try:
  county_data_cases= prep_county_data(df3)
  county_data_deaths= prep_county_data(df4)
  state_data_cases= prep_state_data(df3)
  state_data_deaths= prep_state_data(df4)
  county_sum= prep_county_sum(df3, df4)
  state_sum= prep_state_sum(df3, df4)
  us_trend_cases= prep_us_trend(df3)
  us_trend_deaths= prep_us_trend(df4)
  us_newcases_cases= prep_us_newcases(df3)
  us_newcases_deaths= prep_us_newcases(df4)
  state_newcases_cases=prep_state_newcases(df3)
  state_newcases_deaths=prep_state_newcases(df4)
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
except:
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
  fig = go.Figure(go.Bar(y=countries_data.sort_values(by=[text], ascending=True).index[-10:],
                          x=countries_data.sort_values(by=[text],ascending=True)[text][-10:],
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
  fig = go.Figure(go.Bar(y=d.sort_values(by=[text], ascending=True).index[-10:],
                          x=d.sort_values(by=[text],ascending=True)[text][-10:],
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
                html.P("Worst hit: Cumulative", style={'font-size': '1.2rem'}),
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
          style={'padding':'1%','margin-bottom':'0%'}
          ),
        html.Div([#four columns for R calculation
          html.Div([#chart title
            html.P("Worst hit: New cases",style={'font-size': '1.2rem'})
            ],
            className='row',
            #style={'paddingTop':'2%', 'paddingBottom':'2%'}
            ),
          html.Div([#chart itself
            html.P("Total",style={'font-size': '1rem'}),
            dcc.Graph(figure=make_fig_7_8(country_newcases_cases,df1.columns[-1]), config=conf)
            ],
            className='row'
            ),
          ],
          className='four columns',
          style={'padding':'1%','margin-bottom':'0%'}
          ),
        ],
        className='row',
        style={'paddingTop':'2.5%', 'paddingBottom':'0%'}
        ),
      ],
      className='six columns',
      style={'paddingRight':'1%','paddingLeft':'1%'},
      ),
    ],
    className='row'
    ),
  

  ##BLOCK FOR COUNTRY COMPARISON
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
    style={'padding':'1%', 'background-color':'#F5F5F5', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'2%'}
    ),
  html.Div([#row for body
    html.Div([#six columns for cumulative cases
      html.Div([
        html.P(id="line-header",style = {'margin':0,'font-size':'1.2rem'}),
        html.P('Click for detail', style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
        ], 
        className='row'
        ),
      html.Div([
        dcc.RadioItems(
          id="uom",
          options=[
          {'label': 'Absolute', 'value': 'Abs'},
          {'label': 'per 100k pop.', 'value': 'per100k'}],
          value='per100k',
          labelStyle={'display': 'inline-block'},
          style={'font-size': '1rem', 'float': 'right', 'margin': '1%'}),
        ], 
        className='row'
        ),
      dcc.Graph(id="countries-conf",config=conf,style={'margin':'0%','padding': '2%'}),
      ], 
      className='six columns',
      style={'paddingRight':'2%','paddingLeft':'2%', 'paddingBottom': '4%'}
      ),
    html.Div([#six columns for new cases
      html.Div([
        html.P(id="heatmap-header", style = {'margin':0, 'font-size':'1.2rem'}),
        html.P("Click for detail", style={'color':'#696969','font-size': '1rem', 'font-style':'italic'}),
        ], 
        className='row'
        ),
      html.Div([
        dcc.RadioItems(
          id="uom2",
          options=[
          {'label': 'Absolute', 'value': 'Abs'},
          {'label': 'per 100k pop.', 'value': 'per100k'}],
          value='per100k',
          labelStyle={'display': 'inline-block'},
          style={'font-size': '1rem', 'float': 'right', 'margin': '1%'}),
        ], 
        className='row'),
      dcc.Graph(id='heatmap',config=conf, style={'margin':'0%','padding': '2%'})
      ], 
      className='six columns',
      style={'paddingRight':'2%', 'paddingLeft':'2%','paddingBottom': '4%'}
      ),
    ],
    className='row flex-display',
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
                html.P("Worst hit: Cumulative",style={'font-size': '1.2rem'}),
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
          style={'padding':'1%'}
          ),
        html.Div([#four columns for R calculation
          html.Div([#chart title
            html.P("Worst hit: New cases",style={'font-size': '1.2rem'})
            ],
            className='row'
            ),
          html.Div([#chart itself
            html.P("Total",style={'font-size': '1rem'}),
            dcc.Graph(figure=make_fig_7_8(state_newcases_cases,df3.columns[-1]), config=conf)
            ],
            className='row'
            ),
          ],
          className='four columns',
          style={'padding':'1%'}
          ),
        ],
        className='row',
        ),
      ],
      className='six columns',
      style={'paddingRight':'1%','paddingLeft':'1%'},
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
    s= 0.1*countries_data["Conf100"]
    t=countries_data['text100']
  else:
    s=0.001*countries_data["Confirmed"]
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
    return "New Cases (7 day rolling average)"
  else:
    return "New Deaths (7 day rolling avg)"

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
    s = 0.05*county_sum['Conf100']
    t = county_sum['text100']
  else:
    s = 0.02*(county_sum['Confirmed'])
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

if __name__ == '__main__':
  app.run_server()