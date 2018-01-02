# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 22:01:01 2017

@author: Manuel
"""

from sklearn import preprocessing
from bokeh.plotting import *
from bokeh.models import HoverTool
from bokeh.models import FuncTickFormatter
import pandas as pd
import numpy as np

"""
1) DATA IMPORT
"""
columns = ["addDate","aname","tname","danceability","mode","speechiness",
           "acousticness","instrumentalness","tempo",
           "loudness","energy","liveness",
           "duration_ms","key","valence"]

data = pd.read_csv("data.csv",sep = ";", decimal = ",", encoding = "cp1252")
data = data.loc[:,columns]

"""
2) DATA PREPARATION

prepare data and create new columns for insight visualization
"""

#transform the data into date time
data["addDate"] = pd.to_datetime(data["addDate"])
data["addYM"] = pd.to_datetime(data.addDate.map(lambda x: x.strftime("%Y-%m")))

#group by month
aggr_songs = data.groupby(by = "addYM").size()
#create new column and indicate the number of 
data = data.merge(aggr_songs.to_frame("songsSameMonth"), left_on = "addYM", right_index = True)

x = preprocessing.minmax_scale(data["duration_ms"])
y = preprocessing.minmax_scale(data["key"])
radii = preprocessing.minmax_scale(data["loudness"]*-1)/50
colors = ["#%02x%02x%02x" % (int(l*250), int(g*250), 150) for l,g in zip(data["speechiness"],data["instrumentalness"])]             

          
#add dummy entries for months with 0 additions
months = pd.date_range(data["addYM"].min(),data["addYM"].max(),freq = "MS")
#check if freq is bigger than zero
for month in months:
    if(data[data["addYM"] == month].size == 0):
        tmp = pd.Series({"addYM":month,"songsSameMonth":0})
        data = data.append(tmp, ignore_index = True)
        colors = np.append(colors, np.nan)
        radii = np.append(radii, np.nan)
        x = np.append(x, np.nan)
        y = np.append(y, np.nan)

data_dict = dict(
                addYM = data["addYM"],
                count = data["songsSameMonth"],        
                aname = data["aname"],
                tname = data["tname"],
                x = x,
                y = y,
                radii = radii,
                colors = colors)

data_df = pd.DataFrame(data_dict)
data_df = data_df.sort_values(by = "addYM")

output_file("Visualization/scatter_plot.html")

#tools = "hover,lasso_select,box_select,reset,box_zoom"
hover = HoverTool(tooltips = [
        ("Artist","@aname"),
        ("Track name","@tname")
        ])

TOOLS = "box_select,reset"

def create_plots(data_dict, tools, bar = False):    
    if(bar == True):
        #backtransformation to string to allow for a bar-chart
        data_dict["addYM"] = data_dict["addYM"].apply(lambda x: str(x).split("-01 00:00:00")[0])
        
        x_ticks = []
        i = 0
        for x in data_dict["addYM"]:
            val = str(x).split("-01 00:00:00")[0]
            if(val[-2:] == "01"):
                setx_ticks[i] = val
                i += 1
                
    source = ColumnDataSource(data =data_df)# data_dict)
    first = figure(tools = [hover,TOOLS],
                   x_range =(min(data_dict["x"]),max(data_dict["x"])),
                   y_range = (min(data_dict['y']),max(data_dict['y'])))
    first.circle('x','y',radius = 'radii',fill_color = 'colors', source = source)#,radius = 'radii')#, fill_color = colors)

    ##Add the second plot
    if(bar == True):
        #TODO: set label range
        second = figure(x_range = list(data_dict["addYM"].unique()),tools = [hover,TOOLS])
        second.vbar(x = "addYM",top = "count", width = 0.5, source = source)
        second.xgrid.grid_line_color = None
        #TODO: set label ticks
        second.xaxis.formatter = FuncTickFormatter(code="""
                                        var labels = %s;
                                        return labels[tick];
                                    """ % x_ticks)
    else:
        second = figure(tools = [hover,TOOLS],x_axis_type="datetime")
        second.circle('addYM','count', color = "darkgrey", source = source)
        second.line('addYM','count',source=source)

    #set the grid plot
    p = gridplot([[first,second]])
    return p

p = create_plots(data_dict,[hover,TOOLS], bar = False)
show(p)