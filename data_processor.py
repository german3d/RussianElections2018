import json
import os
import pandas as pd
import pickle
from web_processor import get_raw_data
from viz_processor import assign_colors, assign_hover_info
from config import hierarchy, candidates, data_dirname, data_fname_raw, data_fname_clean, district_fname


def process_json(fname):
    fd_res = {}
    fed_distr = json.load(open(fname))["data"]
    for fd_info in fed_distr:
        fd_name = fd_info["name"]
        reg_names = [x["name"] for x in fd_info["areas"]]
        reg_num = len(reg_names)
        fd_dict = {rn: fn for rn,fn in zip(reg_names, [fd_name]*reg_num)}
        fd_res = {**fd_res, **fd_dict}
    return fd_res


def calculate_useful_metrics(data):
    distributed_comps = ["Число избирательных бюллетеней, выданных избирателям, проголосовавшим досрочно",
    					 "Число избирательных бюллетеней, выданных в помещении для голосования в день голосования",
    					 "Число избирательных бюллетеней, выданных вне помещения для голосования в день голосования"]
    
    listed_comps = ["Число избирателей, включенных в список избирателей"]
    
    filled_comps = ["Число недействительных избирательных бюллетеней",
    				"Число действительных избирательных бюллетеней"]
    
    spoiled_comps = ["Число недействительных избирательных бюллетеней"]
    
    data["listed_abs"]  = data[listed_comps].sum(axis=1)
    data["distributed_abs"] = data[distributed_comps].sum(axis=1)
    data["filled_abs"]  = data[filled_comps].sum(axis=1)
    data["spoiled_abs"] = data[spoiled_comps].sum(axis=1)
    data["stolen_abs"]  = data["distributed_abs"] - data["filled_abs"]
    cols = candidates + ["listed_abs", "distributed_abs", "filled_abs", "stolen_abs", "spoiled_abs"]
    data = data[cols]
    return data


def get_shares_with_hierarchy(data, hierarchy, candidates):
    data = data.rename(columns={k:k+" (абс)" for k in candidates})
    res = {}
    for i in range(len(hierarchy)):
        level = hierarchy[i]
        df = data.groupby(hierarchy[:i+1]).agg("sum")
        df["turnout_share"] = df["distributed_abs"] / df["listed_abs"]
        df["stolen_share"]  = df["stolen_abs"] / df["distributed_abs"]
        df["spoiled_share"] = df["spoiled_abs"] / df["distributed_abs"]
        for cand in candidates:
            df[cand+" (%)"] = df[cand+" (абс)"] / df["filled_abs"]
        res[level] = df
    return res


def process_raw_data(data):
    district = process_json(data_dirname + district_fname)
    data["District"] = data["Region"].apply(lambda x: district.get(x))
    data["Total"] = "Итого"        
    data = data.pivot_table(values="value", index=hierarchy, columns="metric")
    data = calculate_useful_metrics(data=data)
    data = get_shares_with_hierarchy(data=data, hierarchy=hierarchy, candidates=candidates)    
    return data


def get_clean_data():
    if not os.path.isdir(data_dirname):
        os.mkdir(data_dirname)

    if os.path.isfile(data_dirname + data_fname_clean):
        with open(data_dirname + data_fname_clean, "rb") as f:
            data = pickle.load(file=f)
    elif os.path.isfile(data_dirname + data_fname_raw):
        data = pd.read_csv(data_dirname + data_fname_raw, compression="gzip")
        data = process_raw_data(data)        
        with open(data_dirname + data_fname_clean, "wb") as f:
            pickle.dump(obj=data, file=f)
    else:
        data = get_raw_data()
        data.to_csv(data_dirname + data_fname_raw, index=False, compression="gzip")
        data = process_raw_data(data)
        with open(data_dirname + data_fname_clean, "wb") as f:
            pickle.dump(obj=data, file=f)
    data = assign_colors(data)
    data = assign_hover_info(data)
    return data