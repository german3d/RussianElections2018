import json
import pandas as pd


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


def calculate_useful_metrics(df):
    distributed_comps = ["Число избирательных бюллетеней, выданных избирателям, проголосовавшим досрочно",
    					 "Число избирательных бюллетеней, выданных в помещении для голосования в день голосования",
    					 "Число избирательных бюллетеней, выданных вне помещения для голосования в день голосования"]
    
    listed_comps = ["Число избирателей, включенных в список избирателей"]
    
    filled_comps = ["Число недействительных избирательных бюллетеней",
    				"Число действительных избирательных бюллетеней"]
    
    spoiled_comps = ["Число недействительных избирательных бюллетеней"]
    
    df["listed_abs"]  = df[listed_comps].sum(axis=1)
    df["distributed_abs"] = df[distributed_comps].sum(axis=1)    
    df["filled_abs"]  = df[filled_comps].sum(axis=1)
    df["spoiled_abs"] = df[spoiled_comps].sum(axis=1)
    df["stolen_abs"]  = df["distributed_abs"] - df["filled_abs"]
    cols = ["listed_abs", "distributed_abs", "filled_abs", "stolen_abs", "spoiled_abs"]
    df = df[cols]
    return df


def get_shares_with_hierarchy(df_cand, df_stat, hierarchy):
    res = {}
    for i in range(len(hierarchy)):
        level = hierarchy[i]
        idf_cand = df_cand.groupby(hierarchy[:i+1]+["candidate"]).agg("sum").reset_index("candidate")
        idf_stat = df_stat.groupby(hierarchy[:i+1]).agg("sum")
        idf_stat["turnout_share"] = idf_stat["distributed_abs"] / idf_stat["listed_abs"]
        idf_stat["stolen_share"]  = idf_stat["stolen_abs"] / idf_stat["distributed_abs"]
        idf_stat["spoiled_share"] = idf_stat["spoiled_abs"] / idf_stat["distributed_abs"]
        idf_cand = pd.merge(idf_cand, idf_stat, how="left", left_index=True, right_index=True)
        idf_cand["votes_share"] = idf_cand["votes_abs"] / idf_cand["filled_abs"]
        res[level] = idf_cand
    return res
