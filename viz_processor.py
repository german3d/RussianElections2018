import pandas as pd
import numpy as np


def assign_colors(data_dict):
    colors_district = {"Центральный федеральный округ": '#1f77b4',
                       "Приволжский федеральный округ": '#ff7f0e',
                       "Сибирский федеральный округ": '#2ca02c',
                       "Южный федеральный округ": '#d62728',
                       "Северо-Западный федеральный округ": '#9467bd',
                       "Уральский федеральный округ": "#E9E92A",
                       "Дальневосточный федеральный округ": "#F436D1",
                       "Северо-Кавказский федеральный округ": "black",
                       "Территория за пределами РФ": "#B5B1B1",
                       "Город Байконур (Республика Казахстан)": "#2F2D2D"
                     }
    
    colors_cand = {}
    
    for level, data in data_dict.items():
        data["color_cand"] = data["candidate"].apply(lambda x: colors_cand.get(x))
        
        if "District" not in data.index.names:
            data["color_district"] = "blue"
        else:
            ind_district = data.index.get_level_values(level="District")
            data["color_district"] = list(map(lambda x: colors_district.get(x), ind_district))
    return data_dict



def make_hover_info(data, info_type="candidate"):
    if isinstance(data.index, pd.core.indexes.multi.MultiIndex):
        location_name = ["<br>".join(x[1:]) for x in data.index]
    else:
        location_name = data.index

    location_info = [
        """        
        <br>Число выданных бюллетеней: {distributed_abs:,}
        <br>Явка (%): {turnout_share:.1%}
        """.format(distributed_abs=row["distributed_abs"],
                   turnout_share=row["turnout_share"]
                   ) for i,row in data.iterrows()
    ]
             
    if info_type=="candidate":
        node_info = \
        ["""
        <br>
        <br>{candidate}
        <br>Голосов за канд-та (абс): {votes_abs:,}
        <br>Голосов за канд-та (%): {votes_share:.1%}
        """.format(candidate=row["candidate"],
                   votes_abs=row["votes_abs"],
                   votes_share=row["votes_share"]
                  ) for i,row in data.iterrows()
        ]
    
    elif info_type=="location":
        node_info = \
        ["""
        <br>Кол-во испорченных бюллетеней (абс): {spoiled_abs:,},
        <br>Кол-во испорченных бюллетеней (%): {spoiled_share:.1%}
        <br>Кол-во унесенных бюллетеней (абс): {stolen_abs:,},
        <br>Кол-во унесенных бюллетеней (%): {stolen_share:.1%}
        """.format(spoiled_abs=row["spoiled_abs"],
                   spoiled_share=row["spoiled_share"],
                   stolen_abs=row["stolen_abs"],
                   stolen_share=row["stolen_share"]
                   ) for i,row in data.iterrows()
        ]        
    else:
        raise ValueError("Invalid info_type, must be either 'candidate' or 'location'")
    
    info = [x+y+z for x,y,z in zip(location_name, location_info, node_info)]
    return info


def assign_hover_info(data_dict):
    for level, data in data_dict.items():
        data["text_cand"] = make_hover_info(data, info_type="candidate")
        data["text_loc"] = make_hover_info(data, info_type="location")
    return data_dict

