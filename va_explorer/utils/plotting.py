#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 23:56:26 2021

@author: babraham
"""
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots

# ===========PLOTTING PROPERTIES/VARIABLES=====================#
D3 = px.colors.qualitative.D3
PLOTLY = px.colors.qualitative.Plotly
# plotting properties defined below
#======= LOTTING PROPERTIES ==============#
def load_lookup_dicts():
    lookup = dict()
    # dictionary mapping time labels to days (or all)
    lookup["time_dict"] = {"1 week": 7, "1 month": 30, "1 year": 365, "all": "all"}
    # dictionary mapping demographic variable names to corresponding VA survey columns
    lookup["demo_to_col"] = {
        "age group": "age_group",
        "sex": "Id10019",
        "place of death": "Id10058",
    }
    # colors used for plotting
    lookup["color_list"] = [
        "rgb(24,162,185)",
        "rgb(201,0,1)",
        "rgb(8,201,0)",
        "rgb(240,205,21)",
        "rgb(187,21,240)",
        "rgb(250,250,248)",
        "rgb(162,162,162)",
    ]
    # colorscale used for map
    lookup["colorscales"] = {
            "primary": [(0.0, 'rgb(255,255,255)'),
                 (1e-20, 'rgb(0, 147, 146)'),
                 (0.167, 'rgb(0, 147, 146)'),
                 (0.167, 'rgb(57, 177, 133)'),
                 (0.333, 'rgb(57, 177, 133)'),
                 (0.333, 'rgb(156, 203, 134)'),
                 (0.5, 'rgb(156, 203, 134)'),
                 (0.5, 'rgb(233, 226, 156)'),
                 (0.667, 'rgb(233, 226, 156)'),
                 (0.667, 'rgb(238, 180, 121)'),
                 (0.833, 'rgb(238, 180, 121)'),
                 (0.833, 'rgb(232, 132, 113)'),
                 (1.0, 'rgb(232, 132, 113)')],
            "secondary": [(0.0, 'rgb(255,255,255)'),
                  (0.001, 'rgb(230,230,230)'),
                  (1.0, 'rgb(230,230,230)')]
        }
            
    lookup["line_colors"] = {
            "primary": "black", 
            "secondary": "gray"
    }
    # dictionary mapping raw map metrics to human-readable names
    lookup["metric_names"] = {
        "Coded VAs": "Coded VAs",
        "Mean Age of Death": "Mean Age of Death",
        "HIV/AIDS related death": "HIV/AIDS",
        "Diabetes mellitus": "Diabetes Mellitus",
        "Acute resp infect incl pneumonia": "Pneumonia",
        "Other and unspecified cardiac dis": "Other Cardiac",
        "Diarrhoeal diseases": "Diarrhoeal Diseases",
        "Other and unspecified neoplasms": "Unspecified Neoplasm",
        "Renal failure": "Renal Failure",
        "Liver cirrhosis": "Liver Cirrhosis",
        "Digestive neoplasms": "Digestive Neoplasm",
        "Other and unspecified infect dis": "Other",
    }    
    # dictionary mapping place of death names to more human-readable names
    lookup["death_location_names"] = {
        "on_route_to_hospital_or_facility": "En Route to Facility",
        "DK": "Unknown",
        "other_health_facility": "Other Health Facility",
    }    
    # formats for montly, weekly, and yearly dates
    lookup["date_display_formats"] = {
        "week": "%d/%m/%Y",
        "month": "%m/%Y",
        "year": "%Y",
    }

    return lookup

LOOKUP = load_lookup_dicts()

 
# get counts of a categorical field from va data. Field name can either be a 
# column name in the dataframe or a demographic lookup key. Change final column name with display_name argument. 
def get_field_counts(va_df, field_name, full_labels=False, display_name=None):
    if field_name not in va_df.columns:
        # if no matching column in va_df for field name, try lookup in the demo_to_col dict. 
        if not display_name:
            # if no display name provided, use original key
            display_name = field_name
        field_name = LOOKUP['demo_to_col'].get(field_name, field_name)
    assert field_name in va_df.columns
    
    va_df = (va_df[field_name].value_counts()
              .reset_index()
              .assign(index = lambda df: df['index'].str.capitalize())
              .rename(columns={field_name: 'count', 'index': 'group'})
              .assign(percent = lambda df: df.apply(lambda x: np.round(100*x['count']/df['count'].sum(),1), axis=1))
              .assign(label = lambda df: df['percent'].astype(str) + '%')
    )
    if display_name:
        va_df = va_df.rename(columns={'group': display_name})
        
    if full_labels:
        va_df['label'] = va_df['count'].astype(str) + '<br> (' + va_df['percent'].astype(str) + '%)'

    return va_df

#===========DEMOGRAPHIC PLOT LOGIC=========================#
# create a multiplot of va counts by gender, age, and place of death
def demographic_plot(va_df, no_grids=True, column_widths=None, height=600):
    if not column_widths:
        first_width = .4
        column_widths = [first_width, 1 - first_width]
    comb_fig = make_subplots(
        rows=2, cols=2,
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{"colspan": 2}, None]],
        subplot_titles=("Gender","Age Group", "Place of Death"), 
        column_widths=column_widths)

    # gender
    sex_df = get_field_counts(va_df, 'sex', display_name='gender')
    comb_fig.add_trace(go.Bar(name='Gender', x=sex_df['gender'], y=sex_df['count'], text=sex_df['label'], textposition='auto',
               showlegend=False, marker_color=PLOTLY),
        row=1, col=1)

    # age groups
    age_df = get_field_counts(va_df, 'age group', display_name='age_group')
    comb_fig.add_trace(go.Bar(name='Age Group', x=age_df['age_group'], y=age_df['count'], text=age_df['label'], textposition='auto',
               showlegend=False, marker_color=D3),
        row=1, col=2,)

    # place of death
    loc_cts = get_field_counts(va_df, 'place of death', display_name='location')
    lookup = LOOKUP['death_location_names']
    loc_cts['location'] = loc_cts['location'].apply(lambda x: lookup.get(x.lower(), x.capitalize()))
    comb_fig.add_trace(
        go.Bar(name='Place of Death', 
               x=loc_cts['count'], y=loc_cts['location'], orientation='h', showlegend=False,
               text=loc_cts['label'],
            textposition="auto", marker_color=D3[4]),
        row=2, col=1
    )
    if no_grids:
        comb_fig.update_xaxes(showgrid=False)
        comb_fig.update_yaxes(showgrid=False)
        
    return comb_fig.update_layout(height=height)

#===========CAUSE OF DEATH PLOT LOGIC=========================#
# plot top N causes of death in va_data either overall or by factor/demographic
def cause_of_death_plot(va_df, factor, agg_type='counts', N=10):
    figure = go.Figure()
    factor = factor.lower()
    if factor != "all":
        assert factor in ["age group", "sex"]
        factor_col = LOOKUP["demo_to_col"][factor]
        factor_title = "by " + factor.capitalize()
        counts = va_df.pivot_table(
            index="cause",
            columns=factor_col,
            values="id",
            aggfunc=pd.Series.nunique,
            fill_value=0,
            margins=True,
        )
        plot_fn = go.Scatter
    else:
        counts = pd.DataFrame({"All": va_df.cause.value_counts()})
        factor_title = "Overall"
        plot_fn = go.Bar
    counts["cod"] = counts.index
    counts = counts[counts["cod"] != "All"]
    counts = counts.sort_values(by="All", ascending=False).head(N)
    groups = list(set(counts.columns).difference(set(["cod"])))
    if factor != "all":
        groups.remove("All")
    for i, group in enumerate(groups):
        if agg_type != "counts":
            counts[group] = np.round(100 * counts[group] / counts[group].sum(), 1)
        figure.add_trace(
            plot_fn(
                y=counts[group],
                x=counts["cod"],
                name=group.capitalize(),
                orientation="v",
                marker=dict(
                    color=LOOKUP["color_list"][i],
                    line=dict(color="rgb(158,158,158)", width=1),
                ),
            )
        )
    figure.update_layout(
        barmode="stack",
        title_text="Top {} Causes of Death {}".format(N, factor_title),
        xaxis_tickangle=-45,
        yaxis_title="Count" if agg_type == "counts" else "Percent",
    )
    return figure

#========TREND/TIMESERIES PLOT LOGI======================#
def va_trend_plot(va_df, group_period, factor="All"):
    figure = go.Figure()
    group_period = group_period.lower()
    aggregate_title = group_period.capitalize()
    va_df["date"] = pd.to_datetime(va_df["date"])
    va_df["timegroup"] = pd.to_datetime(va_df["date"])
    if group_period == "week":
        va_df["timegroup"] = pd.to_datetime(
            va_df["date"]
            .dt.to_period("W")
            .apply(lambda x: x.strftime("%Y-%m-%d"))
        )
    elif group_period == "month":
        va_df["timegroup"] = pd.to_datetime(
            va_df["date"].dt.to_period("M").apply(lambda x: x.strftime("%Y-%m"))
        )
    elif group_period == "year":
        va_df["timegroup"] = va_df["date"].dt.to_period("Y").astype(str)
    
    dtype = "category" if group_period == "year" else "date"
    
    factor = factor.lower()
    if factor != "all":
        assert factor in LOOKUP["demo_to_col"]
        factor_col = LOOKUP["demo_to_col"][factor]
        trend_counts = va_df.pivot_table(
            index="timegroup",
            columns=factor_col,
            values="id",
            aggfunc=pd.Series.nunique,
            fill_value=0,
            margins=False,
        )
        plot_fn = go.Scatter
    else:
        trend_counts = (
            va_df[["timegroup", "id"]]
            .groupby("timegroup")
            .count()
            .rename(columns={"id": "all"})
        )
        plot_fn = go.Bar
    
    for i, group in enumerate(trend_counts.columns.tolist()):
        figure.add_trace(
            plot_fn(
                y=trend_counts[group],
                x=trend_counts.index,
                name=group.capitalize(),
                marker=dict(
                    color=LOOKUP["color_list"][i],
                    line=dict(color=LOOKUP["color_list"][i], width=1),
                ),
            )
        )
    figure.update_layout(
        title_text="Verbal Autopsies by {}".format(aggregate_title),
        xaxis_title=aggregate_title,
        yaxis_title="Verbal Autopsy Count",
        xaxis_type=dtype,
        xaxis_tickangle=-45,
        xaxis_tickformatstops=[
            dict(
                dtickrange=[None, None],
                value=LOOKUP["date_display_formats"].get(group_period, "%d/%m/%Y"),
            )
        ],
    )
    return figure