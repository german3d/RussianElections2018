import pandas as pd
import numpy as np
import ipywidgets
import cufflinks
import plotly
import plotly.graph_objs as go
from config import metrics_to_russian, hierarchy, candidates
from IPython.display import display


def assign_colors(data_dict):
    colors_district = {"Центральный федеральный округ": '#3778bf', #'#1f77b4',
                       "Приволжский федеральный округ": '#feb308', #'#ff7f0e'
                       "Сибирский федеральный округ": '#7bb274', #'#2ca02c'
                       "Южный федеральный округ": '#fffe40', #'#d62728'
                       "Северо-Западный федеральный округ": '#825f87', #'#9467bd'
                       "Уральский федеральный округ": "#bd6c48", #"#E9E92A"
                       "Дальневосточный федеральный округ": "#8cff9e", #"#F436D1"
                       "Северо-Кавказский федеральный округ": "#3c4142", #"black"
                       "Территория за пределами РФ": "#ffb7ce", #"#B5B1B1"
                       "Город Байконур (Республика Казахстан)": "#a8a495" #"#2F2D2D"
                     }
    for level, data in data_dict.items():
        if "District" not in data.index.names:
            data["color_district"] = "blue"
        else:
            ind_district = data.index.get_level_values(level="District")
            data["color_district"] = list(map(lambda x: colors_district.get(x), ind_district))
    return data_dict


def make_hover_info(data):
    if isinstance(data.index, pd.core.indexes.multi.MultiIndex):
        location_name = ["<br>".join(x[1:]) for x in data.index]
    else:
        location_name = data.index

    node_info = [
        """
        <br>{distributed_abs_alias}: {distributed_abs:,}
        <br>{turnout_share_alias}: {turnout_share:.1%}      
        <br>
        <br>Бабурин Сергей Николаевич: {baburin_share:.1%}
        <br>Грудинин Павел Николаевич: {grudinin_share:.1%}
        <br>Жириновский Владимир Вольфович: {zhirinovsky_share:.1%}
        <br>Путин Владимир Владимирович: {putin_share:.1%}
        <br>Собчак Ксения Анатольевна: {sobchak_share:.1%}
        <br>Сурайкин Максим Александрович: {suraykin_share:.1%}
        <br>Титов Борис Юрьевич: {titov_share:.1%}
        <br>Явлинский Григорий Алексеевич: {yavlinsky_share:.1%}
        """.format(distributed_abs_alias=metrics_to_russian["distributed_abs"],
                   distributed_abs=row["distributed_abs"],
                   turnout_share_alias=metrics_to_russian["turnout_share"],
                   turnout_share=row["turnout_share"],
                   baburin_share=row["Бабурин Сергей Николаевич (%)"],
                   grudinin_share=row["Грудинин Павел Николаевич (%)"],
                   zhirinovsky_share=row["Жириновский Владимир Вольфович (%)"],
                   putin_share=row["Путин Владимир Владимирович (%)"],
                   sobchak_share=row["Собчак Ксения Анатольевна (%)"],
                   suraykin_share=row["Сурайкин Максим Александрович (%)"],
                   titov_share=row["Титов Борис Юрьевич (%)"],
                   yavlinsky_share=row["Явлинский Григорий Алексеевич (%)"],
                   ) for i,row in data.iterrows()
    ]             
    info = [x+y for x,y in zip(location_name, node_info)]
    return info


def assign_hover_info(data_dict):
    for level, data in data_dict.items():
        data["hover_text"] = make_hover_info(data)
    return data_dict


def make_trace(data, x, y, size, color, text, sizeref, visible=False):
    return go.Scatter(
        x=data[x],
        y=data[y],
        hoverinfo="text",
        visible=visible,
        text=data[text],
        mode="markers",
        marker= go.Marker(
            color=data[color],
            size=np.power(data[size], 0.85), # to make bubble size non-linear
            sizeref=sizeref,
            sizemode="area",
            opacity=0.6,
            line=go.Line(width=1.1)))


def display_df(data, x, y, size, color, text, level, title, **kwargs):
    df = data[level].copy().reset_index()
    for k,v in kwargs.items():
        kwargs[k] = list((v,)) if isinstance(v, str) else v
    district = kwargs.get("district")
    region = kwargs.get("region")
    TEC = kwargs.get("TEC")
    PEC = kwargs.get("PEC")

    if district is not None and "District" in df.columns:
        df = df.loc[df["District"].isin(district)]
    if region is not None and "Region" in df.columns:
        df = df.loc[(df["District"].isin(district)) & (df["Region"].isin(region))]
    if TEC is not None and "TEC" in df.columns:
        df = df.loc[(df["District"].isin(district)) & (df["Region"].isin(region)) & \
                    (df["TEC"].isin(TEC))]
    if PEC is not None and "PEC" in df.columns:
        df = df.loc[(df["District"].isin(district)) & (df["Region"].isin(region)) & \
                    (df["TEC"].isin(TEC)) & (df["PEC"].isin(PEC))]

    x_tickformat = ',.2%' if ("share" in x or "%"in x) else ','
    y_tickformat = ',.2%' if ("share" in y or "%"in y) else ','
    x_axis_style = dict(zeroline=False, ticks='outside', tickformat=x_tickformat)
    y_axis_style = dict(zeroline=False, ticks='outside', tickformat=y_tickformat)    
    sizeref = np.power(df[size].max(), 0.85) / .33e2**2
    plot_data = go.Data()
    plot_data.append(make_trace(df, x, y, size, color, text, sizeref, visible=True))
    layout = go.Layout(
        title=title,
        width=950,
        height=700,
        hovermode="closest",
        xaxis=go.XAxis(x_axis_style, title=metrics_to_russian[x], titlefont=dict(size=12)),
        yaxis=go.YAxis(y_axis_style, title=metrics_to_russian[y], titlefont=dict(size=12)),
        dragmode="pan",
    )        
    df.iplot(kind="bubble",
             mode="markers",
             data=plot_data,
             x=x,
             y=y,
             size=size,
             layout=layout,
             theme="white")


def make_dashboard(data):
    
    def update_from_district(*args):
        i_district = select_district.value
        i_loc = widget_locations.loc[widget_locations["District"].isin(i_district)]
        select_region.options = i_loc.drop_duplicates(["District", "Region"])["Region"].tolist()
        select_region.value = i_loc.drop_duplicates(["District", "Region"])["Region"].tolist()    
    
    
    def update_from_region(*args):
        i_district = select_district.value
        i_region = select_region.value
        i_loc = widget_locations.loc[widget_locations["District"].isin(i_district) & \
                                     widget_locations["Region"].isin(i_region)]    
        select_TEC.options = i_loc.drop_duplicates(subset=["District", "Region", "TEC"])["TEC"].tolist()
        select_TEC.value = i_loc.drop_duplicates(subset=["District", "Region", "TEC"])["TEC"].tolist()

    def update_active_locations(*args):
        i_level = dropdown_level.value
        if i_level=="Total":
            select_district.disabled=True
            select_region.disabled=True
            select_TEC.disabled=True
        elif i_level=="District":
            select_district.disabled=False        
            select_region.disabled=True
            select_TEC.disabled=True
        elif i_level=="Region":
            select_district.disabled=False
            select_region.disabled=False
            select_TEC.disabled=True
        elif i_level=="TEC":
            select_district.disabled=False
            select_region.disabled=False
            select_TEC.disabled=False
        elif i_level=="PEC":
            select_district.disabled=False
            select_region.disabled=False
            select_TEC.disabled=False
            
    widget_locations = data["PEC"].reset_index().drop_duplicates(subset=hierarchy)[hierarchy]

    dropdown_level = ipywidgets.Dropdown(
        options={"Итого":            "Total",
                 "Федеральный округ":  "District", 
                 "Субъект":          "Region",
                 "ТИК":             "TEC",
                 "УИК":             "PEC"
                },
        value="District",
        description="Детализация",
        layout={"width": "50%"}
    )

    dropdown_xaxis = ipywidgets.Dropdown(
        options={v:k for k,v in metrics_to_russian.items()},
        value="turnout_share",
        description="Ось X",
        layout={"width": "50%"}
    )

    dropdown_yaxis = ipywidgets.Dropdown(
        options={v:k for k,v in metrics_to_russian.items()},
        value="Путин Владимир Владимирович (%)",
        description="Ось Y",
        layout={"width": "50%"}
    )

    dropdown_size = ipywidgets.Dropdown(
        options={v:k for k,v in metrics_to_russian.items()},
        value="listed_abs",
        description="Размер",
        style = {"description_width": "30%"},
        layout={"width": "50%"}
    )    
    
    select_district = ipywidgets.SelectMultiple(
        options=widget_locations["District"].unique().tolist(),
        value=widget_locations["District"].unique().tolist(),
        layout={"width": "50%"},
        disabled=False)

    select_region = ipywidgets.SelectMultiple(
        options=widget_locations["Region"].unique().tolist(),
        value=widget_locations["Region"].unique().tolist(),
        layout={"width": "50%"},
        disabled=True)

    select_TEC = ipywidgets.SelectMultiple(
        options=widget_locations.drop_duplicates(["Region", "TEC"])["TEC"].tolist(),
        value=widget_locations.drop_duplicates(["Region", "TEC"])["TEC"].tolist(),
        layout={"width": "50%"},
        disabled=True)

    select_district.observe(update_from_district, "value")
    select_region.observe(update_from_region, "value")
    dropdown_level.observe(update_active_locations, "value")
    
    accordion = ipywidgets.Accordion(children=[select_district, select_region, select_TEC],
                                     selected_index=-1)
    accordion.set_title(0, "Федеральный округ")
    accordion.set_title(1, "Cубъект")
    accordion.set_title(2, "ТИК")
    extra_widgets = [dropdown_level, dropdown_xaxis, dropdown_yaxis, dropdown_size]
    
    out = ipywidgets.interactive_output(display_df,
                                        controls=dict(
                                           data=ipywidgets.fixed(data),
                                           x=dropdown_xaxis,
                                           y=dropdown_yaxis,
                                           size=dropdown_size,
                                           color=ipywidgets.fixed("color_district"),
                                           text=ipywidgets.fixed("hover_text"),
                                           title=ipywidgets.fixed("Результаты выборов Президента РФ 2018"),
                                           level=dropdown_level,
                                           district=select_district,
                                           region=select_region,
                                           TEC=select_TEC)
                                );
        
    display(*extra_widgets, accordion, out)
