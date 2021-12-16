# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 16:05:27 2021

@author: jzaj
"""


##Tutorial
import pandas as pd
import numpy as np
import geopandas as gpd
import requests
import folium
import webbrowser
import json
import altair as alt

##Import 2019 Census Data from Census API Subject Table S1701
url="https://api.census.gov/data/2019/acs/acs5/subject?get=GEO_ID,S1701_C03_001E,S1701_C03_011E,S1701_C03_012E,S1701_C03_021E,S1701_C03_014E,S1701_C03_015E,S1701_C03_016E,S1701_C03_017E,S1701_C03_018E,S1701_C03_019E,S1701_C03_020E&for=tract:*&in=state:06&in=county:073&key=4ba7f9cfaea8d5fc6308c15b5bb7259054557448"

resposne=requests.request("GET",url)
Census_Data=pd.DataFrame(resposne.json()[1:], columns=resposne.json()[0]) ##Converts to dataframe

#Rename to Human Readbale Columns
Census_Data.rename(columns={'S1701_C03_001E':'Total_Poverty','S1701_C03_011E':'Male_Poverty','S1701_C03_012E':'Female_Poverty','S1701_C03_021E':'White_Alone_Poverty','S1701_C03_014E':'Black_Alone_Poverty',
                       'S1701_C03_015E':'American_Indian_Poverty','S1701_C03_016E':'Asian_Poverty',
                       'S1701_C03_017E':'Pacific_Islander_Poverty','S1701_C03_018E':'Other_Race_Poverty',
                       'S1701_C03_019E':'Two_Or_More_Races_Poverty','S1701_C03_020E':'Hispanic_Or_Latino_Poverty'}, inplace=True)

Demographic_characterisitcs=['Total_Poverty','Male_Poverty','Female_Poverty','White_Alone_Poverty','Black_Alone_Poverty',
                       'American_Indian_Poverty','Asian_Poverty','Pacific_Islander_Poverty','Other_Race_Poverty',
                       'Two_Or_More_Races_Poverty','Hispanic_Or_Latino_Poverty']

for i in Demographic_characterisitcs:
    Census_Data[i]=pd.to_numeric(Census_Data[i])
    
#Import shape file this is 2010 Census tracts
arc_map = gpd.read_file('C:\\Users\\Jzaj\\OneDrive - San Diego Association of Governments\\Desktop\\SDG Data\\Census_Tract/cb_2018_06_tract_500k.shp')
merged = arc_map.merge(Census_Data, how='left', left_on="AFFGEOID", right_on=Census_Data.GEO_ID)

merged=merged.replace(-666666666.0 ,np.nan)

##Creat Map with Layers for Each Demographic Category
my_map=folium.Map(location=[32.755, -117.0392], zoom_start=9, tiles='CartoDB positron')

folium.Choropleth(
                  geo_data=merged,
                  name="Total Poverty",
                  data=merged,
                  columns=['tract','Total_Poverty'],
                  key_on='feature.properties.tract',
                  fill_color="YlGn",
                  fill_opacity=0.4,
                  line_opacity=0.2,
                  legend_name="Poverty (%)",
                  nan_fill_opacity=0,
                  highlight=True,
                  show=True).add_to(my_map)

Demographic_characterisitcs.remove('Total_Poverty')

for i in Demographic_characterisitcs:
    i_map=folium.Choropleth(geo_data=merged,
                      name=i,
                      data=merged,
                      columns=['tract',i],
                      key_on='feature.properties.tract',
                      fill_color="YlGn",
                      fill_opacity=0.4,
                      line_opacity=0.2,
                      overlay=True,
                      nan_fill_opacity=0,
                      highlight=True,
                      show=False).add_to(my_map)
    for key in i_map._children:
        if key.startswith('color_map'):
            del(i_map._children[key])
    i_map.add_to(my_map)
    
folium.LayerControl().add_to(my_map)
my_map.save("pov.html")
webbrowser.open("pov.html")

##Create Trend Line over time for each Census Tract

url1="https://api.census.gov/data/"
url2="/acs/acs5/subject?get=GEO_ID,S1701_C03_001E&for=tract:*&in=state:06&in=county:073&key=4ba7f9cfaea8d5fc6308c15b5bb7259054557448"

C_data={}

for i in ['2012','2013','2014','2015','2016','2017','2018','2019']:
    url=url1+i+url2
    resposne=requests.request("GET",url)
    df_name = 'Tot_Pov_' + i  
    C_data[df_name]=pd.DataFrame(resposne.json()[1:], columns=resposne.json()[0])
    C_data[df_name].rename(columns={'S1701_C03_001E':'Total_Poverty'},inplace=True)

Tot_Pov_2013=pd.DataFrame()

for i in [Tot_Pov_2012, Tot_Pov_2013]:
    i = C_data[i]
    
    
chart = alt.Chart(merged).mark_line().encode(
        x='GEOID',
        y='Total_Poverty')

chart_2=json.loads(chart.to_json())

marker=folium.Marker(location=[32.755, -117.0392],popup=folium.Popup(max_width=450).add_child(
        folium.Vega(merged[['%Total_Poverty','tract']], width=450, height=250)),)

html= "https://www.sandag.org/"
iframe = folium.element.IFrame(html=html, width=500, height=300)
popup = folium.Popup(iframe, max_width=2650)
popup = folium.Popup(max_width=650)
folium.features.VegaLite(chart_2, height=350, width=650).add_to(popup)
folium.Marker(location=[32.755, -117.0392], popup=popup).add_to(my_map)

marker.add_to(my_map)
