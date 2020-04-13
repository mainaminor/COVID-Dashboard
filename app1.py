import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import datetime as dt
import requests
from bs4 import BeautifulSoup as bs
from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#external_stylesheets = ['https://codepen.io/mainaminor/pen/wvaOEmY.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, 
  meta_tags=[{"name": "viewport", "content": "width=device-width"}]
  )
server = app.server

################################################
#### DATA FOR WORLDWIDE ANALYSES ###############
################################################

url_1='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_2='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
df1=pd.read_csv(url_1)
df2=pd.read_csv(url_2)

df1=df1.groupby(by="Country/Region").sum()
df1.drop(labels=["Lat", "Long"], axis=1, inplace=True)
df1.loc[:,:str(df1.columns[-1])]=np.clip(df1.loc[:,:str(df1.columns[-1])], a_min=0, a_max=None)
df1.rename(index={"US": 'United States of America'}, inplace=True)

df2=df2.groupby(by="Country/Region").sum()
df2.drop(labels=["Lat", "Long"], axis=1, inplace=True)
df2.loc[:,:str(df2.columns[-1])]=np.clip(df2.loc[:,:str(df2.columns[-1])], a_min=0, a_max=None)
df2.rename(index={"US": 'United States of America'}, inplace=True)

df_p=pd.read_csv("worldpop.csv").set_index("Location")

t=df1.merge(df_p, left_index=True, right_index=True)
t2=df2.merge(df_p, left_index=True, right_index=True)

for i in list(t.index):
  t.loc[i, :df1.columns[-1]]=t.loc[i, :df1.columns[-1]]*100/t["PopTotal"][i]
for i in list(t2.index):
  t2.loc[i, :df2.columns[-1]]=t2.loc[i, :df2.columns[-1]]*100/t2["PopTotal"][i]


#Countries for map

countries=pd.read_csv('countries.csv').set_index("name")


countries=countries.merge(df1[df1.columns[-1]], left_index=True, right_index=True)
countries.rename(columns={df1.columns[-1]: "Confirmed"}, inplace=True)
countries=countries.merge(df2[df2.columns[-1]], left_index=True, right_index=True)
countries.rename(columns={df2.columns[-1]: "Deaths"}, inplace=True)
countries=countries.merge(df_p["PopTotal"], left_index=True, right_index=True)
countries["Conf100"]=round(countries["Confirmed"]*100/countries["PopTotal"])
countries["Deaths100"]=round(countries["Deaths"]*100/countries["PopTotal"])
countries["Mortality"]=round(countries["Deaths"]*100/countries["Confirmed"],2)
countries["text"]= countries.index +'<br>' + "Cases: " + countries["Confirmed"].astype('str') + '<br>' + "Deaths: "+ countries["Deaths"].astype('str')
countries["text100"]= countries.index +'<br>' + "Cases: " + countries["Conf100"].astype('str') + '<br>' + "Deaths: "+ countries["Deaths100"].astype('str') 

##country='Italy'
li=[]
current=df1.columns[-1]
#latest=df1[df1.index==country][current].values[0]

options = []
for tic in df1.index:
  options.append({'label':tic, 'value':tic})

##HEATMAP##
#5d rolling avg per 100k cases
scr_5d=pd.DataFrame(index=t.index,columns=list(df1.columns[5:]))
for i in range(len(df1.columns)-5):
    #print(i+1)
    f=(t[t.columns[i+5]]-t[t.columns[i]])/5
    scr_5d[scr_5d.columns[i]]=f
    
#5d rolling avg per 100k deaths
sdr_5d=pd.DataFrame(index=t2.index,columns=list(df2.columns[5:]))
for i in range(len(df2.columns)-5):
    #print(i+1)
    f=(t2[t2.columns[i+5]]-t2[t2.columns[i]])/5
    sdr_5d[sdr_5d.columns[i]]=f

################################################
#### DATA FOR USA ANALYSES #####################
################################################

now = dt.datetime.now()
change= dt.timedelta(days=-1.09)

url_3='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}-2020.csv'.format((now+change).strftime("%m-%d"))
df_us=pd.read_csv(url_3)
df_us=df_us[df_us.loc[:,"Country_Region"]=="US"]
df_us["text"]= df_us['Admin2'] + ', '+ df_us["Province_State"] + '<br>Cases: ' + (df_us['Confirmed']).astype(str)+ '<br>Deaths: ' + (df_us['Deaths']).astype(str)

us_pop=pd.read_csv('us_pop.csv')

us_all=df_us.merge(us_pop[["FIPS", "CTYNAME", "POPESTIMATE2019", "Abbreviation"]], on="FIPS")
us_all["Mortality"]=round(us_all["Deaths"]*100/us_all["Confirmed"],2)
us_all["Conf100"]=us_all["Confirmed"]*100000/us_all["POPESTIMATE2019"]
us_all["Deaths100"]=us_all["Deaths"]*100000/us_all["POPESTIMATE2019"]
us_all["Ctylabel"]=us_all["Admin2"]+ ", "+us_all["Abbreviation"]
us_all["text100"]= us_all['Admin2'] + ', '+ us_all["Province_State"] + '<br>Cases: ' + (round(us_all['Conf100'],1).astype(str))+ '<br>Deaths: ' + (round(us_all['Deaths100'],1).astype(str))

dff=us_all[["Province_State", "Confirmed", "Deaths","POPESTIMATE2019"]].groupby(by="Province_State").sum()
dff["Conf100"]=dff["Confirmed"]*100000/dff["POPESTIMATE2019"]
dff["Deaths100"]=dff["Deaths"]*100000/dff["POPESTIMATE2019"]
dff["Mortality"]=round(dff["Deaths"]*100/dff["Confirmed"],2)




################################################
#### DATA FOR UK ANALYSES ######################
################################################

#Load England Data
url_5='https://www.arcgis.com/sharing/rest/content/items/bc8ee90225644ef7a6f4dd1b13ea1d67/data'
timestamp=pd.read_excel(url_5)["DateVal"][0]
uk_sum=pd.read_excel(url_5)

url_4='https://www.arcgis.com/sharing/rest/content/items/b684319181f94875a6879bbc833ca3a6/data'
uk=pd.read_csv(url_4)
uk.drop(labels=["GSS_CD"], axis=1, inplace=True)
uk.rename(columns={"GSS_NM":"ReportingArea"}, inplace=True)


# Load & append Scotland data
source=requests.get('https://www.gov.scot/publications/coronavirus-covid-19-tests-and-cases-in-scotland/').text
soup=bs(source,'lxml')
tab = soup.find('tbody').text
tablist = tab.split('\t')
tablist2=tablist[0].split('\n')
str_list=list(np.array(tablist2))
str_list = list(filter(None, str_list))
str_list=np.array(str_list)
str_list=np.where(str_list=="*", "4", str_list)
str_list=np.where(str_list=="\xa0", "0", str_list) 
df_y=pd.DataFrame({
                   "ReportingArea":str_list[0::4], 
                   "TotalCases": [i for i in str_list[1::4]]})

uk=uk.append(df_y,ignore_index=True)

#load & append Wales and Northern Ireland data
uk=uk.append(pd.DataFrame({'ReportingArea':['WALES', 'NORTHERN IRELAND'], 
                           'TotalCases':[pd.read_excel(url_5)["WalesCases"].values[0],pd.read_excel(url_5)["NICases"].values[0] ]}),
             ignore_index=True)
uk=uk.set_index("ReportingArea")

#Load UK map data, append Wales & NI centroids

uk_map=pd.read_csv("uk_map.csv").drop(columns="Unnamed: 0")


uk_mapp=uk_map.groupby(by="ReportingArea").mean()


#Load UK Pop data
uk_pop=pd.read_csv("uk_pop.csv").drop(columns="Unnamed: 0")
uk_popp=uk_pop.groupby(by="ReportingArea").sum()

#Define function to convert dirty case entries to clean integers
def convert(val):
    step1=str(val)
    step2 = step1.replace(',','')
    step3= int(step2)
    return step3


#Merge Statistics, map and population data
uk_all=uk.merge(uk_popp, right_index=True, left_index=True)
uk_all.rename(columns={"TotalCases": "Confirmed"}, inplace=True)
uk_all=uk_all.merge(uk_mapp, on="ReportingArea")
uk_all["Confirmed"]=uk_all["Confirmed"].apply(convert)

uk_all["Conf100"]=uk_all["Confirmed"]*100000/uk_all["All ages"]
uk_all["text"]= uk_all.index+ ', '+ '<br>Cases: ' + (uk_all['Confirmed']).astype(str)
uk_all["text100"]= uk_all.index + ', '+ '<br>Cases: ' + (round(uk_all['Conf100'],1).astype(str))


#Create simplified table for comparing local authorities
London= ["Barking and Dagenham",
"Barnet",
"Bexley",
"Brent",
"Bromley",
"Camden",
"Croydon",
"Ealing",
"Enfield",
"Greenwich",
"Hackney",
"Hammersmith and Fulham",
"Haringey",
"Harrow",
"Havering",
"Hillingdon",
"Hounslow",
"Islington",
"Kensington and Chelsea",
"Kingston upon Thames",
"Lambeth",
"Lewisham",
"Merton",
"Newham",
"Redbridge",
"Richmond upon Thames",
"Southwark",
"Sutton",
"Tower Hamlets",
"Waltham Forest",
"Wandsworth",
"Westminster"]

ln=[]
for i in range(len(uk_all.index)):
    if uk_all.index[i] in London:
        ln.append("London")
    else:
        ln.append(uk_all.index[i])

uk_all["ReportingArea2"]=ln

uk_clean=uk_all.groupby("ReportingArea2").sum().drop(["WALES", "NORTHERN IRELAND"])
uk_clean["Conf100"]= uk_clean["Confirmed"]*100000/uk_clean["All ages"]
uk_clean=uk_clean.drop(columns=["long", "lat"])


################################################
#### INITIALISATION OF CHARTS ##################
################################################

#WORLD MAP WITH CONFIRMED CASES
d1 =go.Scattergeo(
    lon=countries["longitude"],
    lat=countries["latitude"],
    text = countries['text'],
    hoverinfo = 'text',
    marker=dict(
        size= np.sqrt(countries["Confirmed"]),
        line_width=0.5,
        sizemode='area'
    )
)

l1=go.Layout(
    #title=go.layout.Title(text="Cases as of {}".format(current))
    #,yaxis_type="log"
    margin={"r":0,"t":0,"l":0,"b":0}
)

fig1=go.Figure(data=d1, layout=l1)



fig1.update_geos(
    visible=True, 
    resolution=110, 
    showcountries=True, 
    countrycolor="grey",
    showsubunits=True, 
    subunitcolor="White",
    lataxis_showgrid=True, 
    lonaxis_showgrid=True
)


#LINE CHART OF CONFIRMED CASES

d3=[{
    'x': df1.columns,
     'y': df1[df1.index==country].values[0],
     'name': country
} for country in li]
l3=go.Layout(
    #title=go.layout.Title(text="Cases as of {}".format(current))
    #,yaxis_type="log"
    margin={"r":0,"t":0,"l":0,"b":0},
    legend={'x':0.01, 'y':0.98},
)
fig3=go.Figure(data=d3,layout=l3)



#HEATMAP

d4=go.Heatmap(
        z=scr_5d.loc[li],
        x=scr_5d.columns,
        y=li,
        colorscale='Blues', 
        colorbar={"thickness":10, "tickfont":{"size":10}},
        )


l4=go.Layout(
    #title='New infections per day (5d rolling avg)',
    margin={"r":0,"t":30,"l":0,"b":0},
    yaxis={"tickfont":{"size":10}},
    xaxis={"tickfont":{"size":10}}
    #xaxis_nticks=36,
    #zaxis_type="log"
)
fig4=go.Figure(data=d4,layout=l4)



#USA MAP

d5= go.Scattergeo(
    lon = us_all['Long_'],
    lat = us_all['Lat'],
    text = us_all['text'],
    hoverinfo = 'text',
    marker = dict(
            size = 0.2*(us_all['Confirmed']),
            line_width=0.5,
            sizemode = 'area'
        )

)

l5=go.Layout(margin={"r":0,"t":0,"l":0,"b":0})

fig5 = go.Figure(data=d5, layout=l5)

fig5.update_geos(
    visible=True, 
    resolution=110, 
    scope="usa",
    showcountries=True, 
    countrycolor="Grey",
    showsubunits=True, 
    subunitcolor="White"
)


#UK Map

d6=go.Scattermapbox(
    lon = uk_all['long'],
    lat = uk_all['lat'],
    text = uk_all['text'],
    hoverinfo = 'text',
    marker = dict(
            size = 5*np.sqrt(uk_all['Confirmed']),
            #line_width=0.5,
            sizemode = 'area',
        symbol = 'circle'
        ))

l6=go.Layout(
  mapbox_style="carto-positron",
  mapbox=dict(
    bearing=0,
    center=go.layout.mapbox.Center(
    lat=54.3781,
    lon=-3.4360
    ),
    pitch=0,
    zoom=4),
  margin={"r":0,"t":0,"l":0,"b":0},
  #autosize=False,
  #width=500,
  #height=500
 )

fig6=go.Figure(data=d6, layout=l6)


#State total cases
fig7 = make_subplots(specs=[[{"secondary_y": True}]])

fig7.add_trace(
    go.Bar(x=dff.sort_values(by=['Confirmed'], ascending=False).index[:10],
                       y=dff.sort_values(by=['Confirmed'], ascending=False)["Confirmed"][:10],
                        name="Cases"
                       #orientation='h'
                      ),
                 secondary_y=False
               )

fig7.add_trace(
    go.Scatter(x=dff.sort_values(by=['Confirmed'],ascending=False).index[:10], 
               y=dff.sort_values(by=['Confirmed'],ascending=False)["Mortality"][:10], 
               name="Mortality (%)"
              ),
    secondary_y=True,
)

fig7.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, 
                   margin={"r":0,"t":0,"l":0,"b":0},
                   legend={'x':-0.01, 'y':1.2,'orientation':"h"},
                   height=250
                  )

#County total cases
fig8 = make_subplots(specs=[[{"secondary_y": True}]])

fig8.add_trace(go.Bar(x=us_all.sort_values(by=['Confirmed'],ascending=False)["Ctylabel"][:10],
                       y=us_all.sort_values(by=['Confirmed'],ascending=False)["Confirmed"][:10],
                      name="Cases"
                       #orientation='h'
                      ),
               secondary_y=False,
               )

fig8.add_trace(
    go.Scatter(x=us_all.sort_values(by=['Confirmed'],ascending=False)["Ctylabel"][:10], 
               y=us_all.sort_values(by=['Confirmed'],ascending=False)["Mortality"][:10], 
               name="Mortality (%)"
              ),
    secondary_y=True,
)

fig8.update_layout(xaxis_showgrid=False, yaxis_showgrid=False,
                  margin={"r":0,"t":0,"l":0,"b":0},
                  legend={'x':-0.01, 'y':1.2,'orientation':"h"},
                  height=250
                  )

#Cases by Country (UK)
fig9 = make_subplots(specs=[[{"secondary_y": True}]])

fig9.add_trace(
    go.Bar(x=["England", "Scotland", "Wales", "Northern Ireland"],
           y=[uk_sum["EnglandCases"][0],uk_sum["ScotlandCases"][0],uk_sum["WalesCases"][0],uk_sum["NICases"][0]],
             name="Cases",
                       #orientation='h'
                      ),
                 secondary_y=False
               )

fig9.add_trace(
    go.Scatter(x=["England", "Scotland", "Wales", "Northern Ireland"],
           y=[round(uk_sum["EnglandDeaths"][0]*100/uk_sum["EnglandCases"][0],2),
              round(uk_sum["ScotlandDeaths"][0]*100/uk_sum["ScotlandCases"][0],2),
              round(uk_sum["WalesDeaths"][0]*100/uk_sum["WalesCases"][0],2),
              round(uk_sum["NIDeaths"][0]*100/uk_sum["NICases"][0],2)],
               name="Mortality (%)"
              ),
    secondary_y=True,
)

fig9.update_layout(xaxis_showgrid=False, yaxis_showgrid=False,
                  margin={"r":0,"t":0,"l":0,"b":0},
                  legend={'x':-0.01, 'y':1.2,'orientation':"h"},
                  height=250)


#Reporting Area total cases per 100k
d10=go.Bar(x=uk_clean.sort_values(by=['Confirmed'], ascending=False).index[:10],
                       y=uk_clean.sort_values(by=['Confirmed'],ascending=False)["Confirmed"][:10],
                       #orientation='h'
                      )

l10=go.Layout(
  height=300,
  margin={"r":0,"t":0,"l":0,"b":0}
  )

fig10=go.Figure(data=d10, layout=l10)

#Cases by Country

fig11= make_subplots(specs=[[{"secondary_y": True}]])


fig11.add_trace(go.Bar(x=countries.sort_values(by="Confirmed", ascending=False).index[:10],
                       y=countries.sort_values(by="Confirmed", ascending=False)["Confirmed"][:10],
                       #orientation='h',
                     name="Cases"
                      ),
              secondary_y=False,
               )
fig11.add_trace(
    go.Scatter(x=countries.sort_values(by="Confirmed", ascending=False).index[:10], 
               y=countries.sort_values(by="Confirmed", ascending=False)["Mortality"][:10], 
               name="Mortality (%)"
              ),
    secondary_y=True,
)

fig11.update_layout(xaxis_showgrid=False, 
                    yaxis_showgrid=False,
                   margin={"r":0,"t":0,"l":0,"b":0},
                   legend={'x':-0.01, 'y':1.15,'orientation':"h"},
                   height=300)


#Deaths by Country

d12 = d=go.Bar(x=countries.sort_values(by="Deaths", ascending=False).index[:10],
            y=countries.sort_values(by="Deaths", ascending=False)["Deaths"][:10])

l12=go.Layout(
  height=300,
  margin={"r":0,"t":0,"l":0,"b":0}
  )

fig12=go.Figure(data=d12, layout=l12)


################################################
#### APP LAYOUT  ###############################
################################################


app.layout = html.Div([
## DIV BLOCK FOR HEADERS ETC
  html.Div([
    html.H5('COVID-19 as of {}'.format(str(df1.columns[-1]))),       
    html.P('Data Source: Johns Hopkins Univerity. Data relies upon publicly available information from multiple sources, that does not always agree',style={'font-size': '1rem','color':'#696969'})
    ], 
    className='row', 
    style={'marginbottom':'25px','padding':'1%'},
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
          #id='cases', 
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
          #id='deaths',
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
          #id='mort',
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%','border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        ],
        #id="info-container", 
        className='row flex-display', 
        #style={'padding':'2%'}
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
              style={'font-size': '1rem'},
            ),
            ],
            className='four columns'
            ),
          ], 
          className='row'),
        dcc.Graph(id= "globe",figure = fig1)
        ],
        className='row flex-display',
        style={'padding':'1.5%'}
        ),
      ],
      className='seven columns flex-display',
      style={'margin':'0','padding': '2%'},
      ),
      html.Div([
        html.Div([
          html.Div([
            html.Div([
              html.P('Worst-hit countries: cases',
                className='eight columns',
                style={'font-size': '1.5rem'}),
              html.Div([
                dcc.RadioItems(
                  id="uom-country-cases",
                  options=[
                  {'label': 'Absolute', 'value': 'Abs'},
                  {'label': 'per 100k pop.', 'value': 'per100k'}],
                  value='Abs',
                  labelStyle={'display': 'inline-block'}
                  )
                ], 
                className='four columns', 
                style={'font-size': '1rem'}
                ),
              ],
              className='row'),
            dcc.Graph(id='country-cases', figure=fig11,
              #style={'margin':'2%','padding': '0%'}
              #responsive='true',
              #className='pretty_container'
              ),
            ], 
            className="twelve columns",
            style={'margin':'0','padding': '2%'},
            ),
          html.Div([
            html.Div([
              html.P('Worst-hit countries: deaths',
                className='eight columns',
                style={'font-size': '1.5rem'}),
              html.Div([
                dcc.RadioItems(
                  id="uom-country-deaths",
                  options=[
                  {'label': 'Absolute', 'value': 'Abs'},
                  {'label': 'per 100k pop.', 'value': 'per100k'}],
                  value='Abs',
                  labelStyle={'display': 'inline-block'}
                  )
                ], 
                className='four columns', 
                style={'font-size': '1rem'}
                ),
              ], 
              className='row'),
            dcc.Graph(id='country-deaths', figure=fig12,
              style={'margin':'2%','padding': '0%'}
              #responsive='true',
              #className='pretty_container'
              )
            ], 
            className='twelve columns',
            style={'margin':'0', 'padding': '2%'},
            )
          ], className='row')
        ],
        className='five columns flex-display',
        style={'margin':'0','padding': '2%'}
        ),
        ],
        className='row flex-display',
        #style={'height':'800px'}
        ),
html.Div([
  html.H5('Trend since January 2020')
  ],       
  className='row', 
  style={'marginbottom':'25px','padding':'1%'}
  ),    
  html.Div([
    html.Div([
      html.Div([
        html.H6('Select countries for comparison', 
          style={'font-size': '1.5rem'}
          ),
          #html.P('Type name or select from dropdown'),
        dcc.Dropdown(
          id='country-select',
          options = options,
          value = countries.sort_values(by="Confirmed", ascending=False).index[:10],
          multi = True)
        ], 
        className="eight columns", 
        style={'font-size': '1rem'}
        ),
      html.Div([
        html.H6('Trend', 
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
        style={'font-size': '1rem'}
        ),
      ], 
      className='row flex-display', 
      style={'padding':'1%', 'background-color':'#F5F5F5', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey', 'margin':'1%'}
      ),
    html.Div([
      html.Div([
        html.H6("New Cases/Deaths",
          style = {'font-size':'1.5rem'}),
        html.H6("per 100k pop, 5d rolling average",
          style = {'font-size':'1rem'}),
        dcc.Graph(id='heatmap',figure=fig4, style={'margin':'0%','padding': '2%'})
        ], 
        className='six columns',style={'padding':'2%'}
        ),
      html.Div([
        html.H6("Cumulative Cases/Deaths",
          style = {'font-size':'1.5rem'}),
        dcc.RadioItems(
          id="uom",
          options=[
          {'label': 'Absolute', 'value': 'Abs'},
          {'label': 'per 100k pop.', 'value': 'per100k'}],
          value='Abs',
          labelStyle={'display': 'inline-block'},
          style={'font-size': '1rem'}),
        dcc.Graph(id="countries-conf",figure=fig3,style={'margin':'0%','padding': '2%'} 
          ),
        ], 
        className='six columns',style={'padding':'2%'}),
      ],
      className='row flex-display',
      style={'padding':'1%'},
      )
    ]
    ),
#BLOCK FOR US
  html.Div([
    html.H5('USA: as of {}'.format(str(df1.columns[-1]))),       
    html.P('Data Source: Johns Hopkins Univerity. Data relies upon publicly available information from multiple sources, that does not always agree',style={'font-size': '1rem','color':'#696969'})
    ], 
    className='row', 
    style={'marginbottom':'25px','padding':'1%'}
    ),
    html.Div([
      html.Div([
          html.Div([
            html.Div([
                html.P('Cases:', 
                  style={'color':'#696969', 'font-size': '1rem'}
                  ),
                html.P('{}'.format(f'{us_all["Confirmed"].sum():,}'), 
                  style={'font-size': '1.5rem'}
                  )
                ],
                #id='cases', 
                className='four columns',
                style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
                ),
            html.Div([
              html.P('Deaths:', 
                style={'color':'#696969','font-size': '1rem'}
                ),
              html.P('{}'.format(f'{us_all["Deaths"].sum():,}'), 
                style={'font-size': '1.5rem'}
                )
              ],
              #id='deaths',
              className='four columns',
              style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
              ),
            html.Div([
              html.P('Avg mortality:', 
                style={'color':'#696969','font-size': '1rem'}
                ),
              html.P('{} % '.format(round(100*us_all["Deaths"].sum()/us_all["Confirmed"].sum(),2)), 
                style={'font-size': '1.5rem'}
                )
              ], 
              #id='mort',
              className='four columns',
              style={'background-color':'#F5F5F5','padding':'1%','border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
              ),
            ],
            #id="info-container", 
            className='row', 
            #style={'padding':'2%'}
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
                  style={'font-size': '1rem'}
                  ),
                ], 
                className='four columns'
                )
              ], 
              className='row'),
            dcc.Graph(id= "US map",figure = fig5)
            ],
            className='row flex-display',
            style={'padding':'1.5%'}
            ),
          ],
          className='seven columns flex-display',
          style={'margin':'0','padding': '2%'},
          ),
      html.Div([
        html.Div([
          html.Div([
            html.Div([
              html.P('Worst-hit counties',
                className='eight columns',
                style={'font-size': '1.5rem'}),
              html.Div([
                dcc.RadioItems(
                  id="uom-county-cases",
                  options=[
                  {'label': 'Absolute', 'value': 'Abs'},
                  {'label': 'per 100k pop.', 'value': 'per100k'}],
                  value='Abs',
                  labelStyle={'display': 'inline-block'}
                  )
                ], 
                className='four columns', 
                style={'font-size': '1rem'}
                ),
              ], className='row'),
            dcc.Graph(id='county-cases', figure=fig8,
              style={'margin':'0%','padding': '2%'}
                #responsive=True,
                #className='pretty_container'
                )
            ], 
            className='twelve columns',
            style={'margin':'0', 'padding': '2%'},
            ),
          html.Div([
            html.Div([
              html.P('Worst-hit states',
                className='eight columns',
                style={'font-size': '1.5rem'}),
              html.Div([
                dcc.RadioItems(
                  id="uom-state-cases",
                  options=[
                  {'label': 'Absolute', 'value': 'Abs'},
                  {'label': 'per 100k pop.', 'value': 'per100k'}],
                  value='Abs',
                  labelStyle={'display': 'inline-block'}
                  )
                ], 
                className='four columns', 
                style={'font-size': '1rem'}
                ),
              ], className='row'),
            dcc.Graph(id='state-cases', figure=fig7,
              style={'margin':'0%','padding': '2%'}
              #responsive=True,
              #className='pretty_container'
              ),
            ], 
            className="twelve columns",
            style={'margin':'0','padding': '2%'},
            ),
          ], 
          className='row'
          ),
        ],
        className='five columns flex-display',
        style={'margin':'0','padding': '2%'}
        ),
      ],
      className='row flex-display'
      ),
#BLOCK FOR UK 
html.Div([
  html.H5('UK: as of {}'.format(timestamp.strftime("%m/%d/%y"))),       
  html.P('Data Source: Public Health England',style={'font-size': '1rem','color':'#696969'})
  ], 
  className='row', 
  style={'marginbottom':'25px','padding':'1%'}
  ),
  html.Div([
    html.Div([
      html.Div([
        html.Div([
          html.P('Cases:', 
            style={'color':'#696969', 'font-size': '1rem'}
            ),
          html.P('{}'.format(f'{uk_sum["TotalUKCases"][0]:,}'), 
            style={'font-size': '1.5rem'}
            )
          ],
          #id='cases', 
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        html.Div([
          html.P('Deaths:', 
            style={'color':'#696969','font-size': '1rem'}
            ),
          html.P('{}'.format(f'{uk_sum["TotalUKDeaths"][0]:,}'), 
            style={'font-size': '1.5rem'}
            )
          ],
          #id='deaths',
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%', 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        html.Div([
          html.P('Avg mortality:', 
            style={'color':'#696969','font-size': '1rem'}
            ),
          html.P('{} % '.format(round(100*uk_sum["TotalUKDeaths"][0]/uk_sum["TotalUKCases"][0],2)), 
            style={'font-size': '1.5rem'}
            )
          ], 
          #id='mort',
          className='four columns',
          style={'background-color':'#F5F5F5','padding':'1%','border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','margin':'0.5%'}
          ),
        ],
        #id="info-container", 
        className='row', 
        #style={'padding':'2%'}
        ),
      html.Div([
        html.Div([
          html.Div([
            html.P('Statistics by local authority',
              style={'margin-bottom':'0', 'paddingBottom':'0','font-size': '1.5rem'}),
            html.P('Click for detail',
              style={'color':'#696969','font-size': '1rem', 'font-style':'italic'})
            ], className='eight columns'
            ),
          html.Div([
            dcc.RadioItems(
                id="uom-uk-map",
                options=[
                {'label': 'Absolute', 'value': 'Abs'},
                {'label': 'per 100k pop.', 'value': 'per100k'}],
                value='Abs',
                labelStyle={'display': 'inline-block'},
            style={'font-size': '1rem'},
            ),
            ], className='four columns'
            ),
          ], className='row'),
          dcc.Graph(id= "UK map",figure = fig6)
          ],
          className='row flex-display',
          style={'padding':'1.5%'}
          ),
        ],
        className='seven columns flex-display',
        style={'margin':'0','padding': '2%'}
        ),
    html.Div([
      html.Div([
        html.Div([
          html.Div([
            html.P('Worst-hit local authorities',
              className='eight columns',
              style={'font-size': '1.5rem'}),
            html.Div([
              dcc.RadioItems(
                id="uom-area-cases",
                options=[
                {'label': 'Absolute', 'value': 'Abs'},
                {'label': 'per 100k pop.', 'value': 'per100k'}],
                value='Abs',
                labelStyle={'display': 'inline-block'},
                style={'font-size': '1rem'},
                ),
              ],
              className='four columns'
              )
            ],
            className='row'
            ),
          dcc.Graph(id='area-cases', figure=fig10,
            style={'margin':'0%','padding': '2%'}
            #responsive=True,
            #className='pretty_container'
            )
          ], 
          className='twelve columns',
          style={'margin':'0', 'padding': '2%'},
          ),
        html.Div([
          html.Div([
            html.P('Summary by country',
              className='eight columns',
              style={'font-size': '1.5rem'}),
            html.Div([
              dcc.RadioItems(
                id="uom-uk-cases",
                options=[
                {'label': 'Absolute', 'value': 'Abs'},
                {'label': 'per 100k pop.', 'value': 'per100k'}],
                value='Abs',
                labelStyle={'display': 'inline-block'},
                style={'font-size': '1rem'},
                ),
              ],
              className='four columns'
              )
            ],
            className='row'
            ),
          dcc.Graph(id='uk-cases', figure=fig9,
            style={'margin':'0%','padding': '2%'}
            #responsive=True,
            #className='pretty_container'
            ),
          ], 
          className="twelve columns",
          style={'margin':'0','padding': '2%'},
          ),
          ], 
          className='row')
      ],
      className='five columns flex-display',
      style={'margin':'0','padding': '2%'}
      ),
    ],
    className='row flex-display'
    ),
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
    lon=countries["longitude"],
    lat=countries["latitude"],
    text = countries['text100'],
    hoverinfo = 'text',
    marker=dict(
        size= 20*np.sqrt(countries["Conf100"]),
        line_width=0.5,
        sizemode='area'
    )))
  else:
    d=d1

  fig1=go.Figure(data=d)
  fig1.update_layout(l1)

  fig1.update_geos(
    visible=True, 
    resolution=110, 
    showcountries=True, 
    countrycolor="grey",
    showsubunits=True, 
    subunitcolor="White",
    lataxis_showgrid=True, 
    lonaxis_showgrid=True
)
  return fig1
#Callback for Countries Cases UoM
@app.callback(
  Output('country-cases', 'figure'),
  [Input('uom-country-cases', 'value')])
def update_chart(units):
  if units == "per100k":
    fig11= make_subplots(specs=[[{"secondary_y": True}]])
    fig11.add_trace(go.Bar(x=countries.sort_values(by="Conf100", ascending=False).index[:10], 
                       y=countries.sort_values(by="Conf100", ascending=False)["Conf100"][:10],
                       name="Cases"), secondary_y=False),
    fig11.add_trace(go.Scatter(x=countries.sort_values(by="Conf100", ascending=False).index[:10], 
                      y=countries.sort_values(by="Conf100", ascending=False)["Mortality"][:10], 
                      name="Mortality (%)"), secondary_y=True),
    fig11.update_layout(xaxis_showgrid=False,yaxis_showgrid=False, margin={"r":0,"t":0,"l":0,"b":0},legend={'x':-0.01, 'y':1.15,'orientation':"h"})
  else:
    fig11= make_subplots(specs=[[{"secondary_y": True}]])
    fig11.add_trace(go.Bar(x=countries.sort_values(by="Confirmed", ascending=False).index[:10], 
                       y=countries.sort_values(by="Confirmed", ascending=False)["Confirmed"][:10],
                       name="Cases"), secondary_y=False),
    fig11.add_trace(go.Scatter(x=countries.sort_values(by="Confirmed", ascending=False).index[:10], 
                      y=countries.sort_values(by="Confirmed", ascending=False)["Mortality"][:10], 
                      name="Mortality (%)"), secondary_y=True),
    fig11.update_layout(xaxis_showgrid=False,yaxis_showgrid=False, margin={"r":0,"t":0,"l":0,"b":0},legend={'x':-0.01, 'y':1.15,'orientation':"h"})
  return fig11

#Callback for Countries deaths UoM
@app.callback(
  Output('country-deaths', 'figure'),
  [Input('uom-country-deaths', 'value')])
def update_chart(units):
  if units=="per100k":
    d=go.Bar(x=countries.sort_values(by="Deaths100", ascending=False).index[:10],
            y=countries.sort_values(by="Deaths100", ascending=False)["Deaths100"][:10])
  else:
    d=d12

  fig12=go.Figure(data=d)
  fig12.update_layout(l12)
  return fig12

#Callback for Line Charts
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
          'x': df1.columns,
          'y': df1[df1.index==country].values[0],
          'name': country
          } for country in li]
          fig3=go.Figure(data=d3,layout=l3)
      else:
          d3=[{
          'x': df1.columns,
          'y': t[t.index==country].values[0],
          'name': country
          } for country in li]
          fig3=go.Figure(data=d3,layout=l3)
    else:
      if uom =="Abs":
            d3=[{
            'x': df2.columns,
            'y': df2[df2.index==country].values[0],
            'name': country
            } for country in li]
            fig3=go.Figure(data=d3,layout=l3)
      else:
          d3=[{
          'x': df2.columns,
          'y': t2[t2.index==country].values[0],
          'name': country
          } for country in li]
          fig3=go.Figure(data=d3,layout=l3)

    return fig3

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
        z=sdr_5d.loc[li],
        x=sdr_5d.columns,
        y=li,
        colorscale='Blues',
        colorbar={"thickness":10, "tickfont":{"size":10}},
        )
        fig4=go.Figure(data=data,layout=l4)
    else:
        data=go.Heatmap(
        z=scr_5d.loc[li],
        x=scr_5d.columns,
        y=li,
        colorscale='Blues',
        colorbar={"thickness":10, "tickfont":{"size":10}},
        )
        fig4=go.Figure(data=data,layout=l4)
    return fig4

#Callback for US map UoM
@app.callback(
  Output('US map', 'figure'),
  [Input('uom-us-map', 'value')])
def update_chart(units):
  if units=='per100k':
    d=go.Scattergeo(
    lon = us_all['Long_'],
    lat = us_all['Lat'],
    text = us_all['text100'],
    hoverinfo = 'text',
    marker = dict(
            size = 0.6*us_all['Conf100'],
            line_width=0.5,
            sizemode = 'area'
        ))
  else:
    d=d5
  fig5=go.Figure(data=d)
  fig5.update_layout(l5)
  fig5.update_geos(
    visible=True, 
    resolution=110, 
    scope="usa",
    showcountries=True, 
    countrycolor="Grey",
    showsubunits=True, 
    subunitcolor="White")

  return fig5

#Callback for States UoM
@app.callback(
  Output('state-cases', 'figure'),
  [Input('uom-state-cases', 'value')])
def update_chart(units):
  if units == "per100k":
    fig7= make_subplots(specs=[[{"secondary_y": True}]])
    fig7.add_trace(go.Bar(x=dff.sort_values(by="Conf100", ascending=False).index[:10], 
                       y=dff.sort_values(by="Conf100", ascending=False)["Conf100"][:10],
                       name="Cases"), secondary_y=False),
    fig7.add_trace(go.Scatter(x=dff.sort_values(by="Conf100", ascending=False).index[:10], 
                      y=dff.sort_values(by="Conf100", ascending=False)["Mortality"][:10], 
                      name="Mortality (%)"), secondary_y=True),
    fig7.update_layout(xaxis_showgrid=False,yaxis_showgrid=False, margin={"r":0,"t":0,"l":0,"b":0},legend={'x':-0.01, 'y':1.2,'orientation':"h"})
  else:
    fig7= make_subplots(specs=[[{"secondary_y": True}]])
    fig7.add_trace(go.Bar(x=dff.sort_values(by="Confirmed", ascending=False).index[:10], 
                       y=dff.sort_values(by="Confirmed", ascending=False)["Confirmed"][:10],
                       name="Cases"), secondary_y=False),
    fig7.add_trace(go.Scatter(x=dff.sort_values(by="Confirmed", ascending=False).index[:10], 
                      y=dff.sort_values(by="Confirmed", ascending=False)["Mortality"][:10], 
                      name="Mortality (%)"), secondary_y=True),
    fig7.update_layout(xaxis_showgrid=False,yaxis_showgrid=False, margin={"r":0,"t":0,"l":0,"b":0},legend={'x':-0.01, 'y':1.2,'orientation':"h"})
  return fig7
#Callback for Counties UoM
@app.callback(
  Output('county-cases', 'figure'),
  [Input('uom-county-cases', 'value')])
def update_chart(units):
  if units == "per100k":
    fig8= make_subplots(specs=[[{"secondary_y": True}]])
    fig8.add_trace(go.Bar(x=us_all.sort_values(by="Conf100", ascending=False)["Ctylabel"][:10], 
                       y=us_all.sort_values(by="Conf100", ascending=False)["Conf100"][:10],
                       name="Cases"), secondary_y=False),
    fig8.add_trace(go.Scatter(x=us_all.sort_values(by="Conf100", ascending=False)["Ctylabel"][:10], 
                      y=us_all.sort_values(by="Conf100", ascending=False)["Mortality"][:10], 
                      name="Mortality (%)"), secondary_y=True),
    fig8.update_layout(xaxis_showgrid=False,yaxis_showgrid=False, margin={"r":0,"t":0,"l":0,"b":0},legend={'x':-0.01, 'y':1.2,'orientation':"h"})
  else:
    fig8= make_subplots(specs=[[{"secondary_y": True}]])
    fig8.add_trace(go.Bar(x=us_all.sort_values(by="Confirmed", ascending=False)["Ctylabel"][:10], 
                       y=us_all.sort_values(by="Confirmed", ascending=False)["Confirmed"][:10],
                       name="Cases"), secondary_y=False),
    fig8.add_trace(go.Scatter(x=us_all.sort_values(by="Confirmed", ascending=False)["Ctylabel"][:10], 
                      y=us_all.sort_values(by="Confirmed", ascending=False)["Mortality"][:10], 
                      name="Mortality (%)"), secondary_y=True),
    fig8.update_layout(xaxis_showgrid=False,yaxis_showgrid=False, margin={"r":0,"t":0,"l":0,"b":0},legend={'x':-0.01, 'y':1.2,'orientation':"h"})
  return fig8

#Callback for UK map UoM
@app.callback(
  Output('UK map', 'figure'),
  [Input('uom-uk-map', 'value')])
def update_chart(units):
  if units == "per100k":
    d=go.Scattermapbox(
    lon = uk_all['long'],
    lat = uk_all['lat'],
    text = uk_all['text100'],
    hoverinfo = 'text',
    marker = dict(
            size = uk_all['Conf100'],
            sizemode = 'area',
        symbol = 'circle'
        ))
  else:
    d=d6
  fig6=go.Figure(data=d)
  fig6.update_layout(l6)

  return fig6
#Callback for UK countries UoM
@app.callback(
  Output('uk-cases', 'figure'),
  [Input('uom-uk-cases', 'value')])
def update_chart(units):
  if units =="per100k":
    fig9 = make_subplots(specs=[[{"secondary_y": True}]])

    fig9.add_trace(
        go.Bar(x=["England", "Scotland", "Wales", "Northern Ireland"],
               y=[round(uk_sum["EnglandCases"][0]*100000/uk_pop["All ages"][uk_pop["ReportingArea"]=="ENGLAND"].values[0],2),
                  round(uk_sum["ScotlandCases"][0]*100000/uk_pop["All ages"][uk_pop["ReportingArea"]=="SCOTLAND"].values[0],2),
                  round(uk_sum["WalesCases"][0]*100000/uk_pop["All ages"][uk_pop["ReportingArea"]=="WALES"].values[0],2),
                  round(uk_sum["NICases"][0]*100000/uk_pop["All ages"][uk_pop["ReportingArea"]=="NORTHERN IRELAND"].values[0],2)],
                 name="Cases",
                           #orientation='h'
                          ),
                     secondary_y=False
                   )

    fig9.add_trace(
        go.Scatter(x=["England", "Scotland", "Wales", "Northern Ireland"],
               y=[round(uk_sum["EnglandDeaths"][0]*100/uk_sum["EnglandCases"][0],2),
                  round(uk_sum["ScotlandDeaths"][0]*100/uk_sum["ScotlandCases"][0],2),
                  round(uk_sum["WalesDeaths"][0]*100/uk_sum["WalesCases"][0],2),
                  round(uk_sum["NIDeaths"][0]*100/uk_sum["NICases"][0],2)],
                   name="Mortality (%)"
                  ),
        secondary_y=True,
    )

    fig9.update_layout(xaxis_showgrid=False, yaxis_showgrid=False,margin={"r":0,"t":0,"l":0,"b":0},legend={'x':-0.01, 'y':1.2,'orientation':"h"},height=250)
  else:
    fig9 = make_subplots(specs=[[{"secondary_y": True}]])

    fig9.add_trace(
        go.Bar(x=["England", "Scotland", "Wales", "Northern Ireland"],
               y=[uk_sum["EnglandCases"][0],uk_sum["ScotlandCases"][0],uk_sum["WalesCases"][0],uk_sum["NICases"][0]],
                 name="Cases",
                           #orientation='h'
                          ),
                     secondary_y=False
                   )

    fig9.add_trace(
        go.Scatter(x=["England", "Scotland", "Wales", "Northern Ireland"],
               y=[round(uk_sum["EnglandDeaths"][0]*100/uk_sum["EnglandCases"][0],2),
                  round(uk_sum["ScotlandDeaths"][0]*100/uk_sum["ScotlandCases"][0],2),
                  round(uk_sum["WalesDeaths"][0]*100/uk_sum["WalesCases"][0],2),
                  round(uk_sum["NIDeaths"][0]*100/uk_sum["NICases"][0],2)],
                   name="Mortality (%)"
                  ),
        secondary_y=True,
    )

    fig9.update_layout(xaxis_showgrid=False, yaxis_showgrid=False,margin={"r":0,"t":0,"l":0,"b":0},legend={'x':-0.01, 'y':1.2,'orientation':"h"}, height=250)

  return fig9


#Callback for UK LA's UoM
@app.callback(
  Output('area-cases', 'figure'),
  [Input('uom-area-cases', 'value')])
def update_chart(units):
  if units == "per100k":
    d=go.Bar(x=uk_clean.sort_values(by=['Conf100'], ascending=False).index[:10],
                       y=uk_clean.sort_values(by=['Conf100'],ascending=False)["Conf100"][:10],
                      )
  else:
    d=d10

  fig10=go.Figure(data=d)
  fig10.update_layout(l10)
  return fig10

if __name__ == '__main__':
	app.run_server()
