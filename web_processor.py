import re
import requests
import time
import pandas as pd
from concurrent import futures
from bs4 import BeautifulSoup
from tqdm import tqdm_notebook


def get_response(url, max_timeout=30, max_retry=100):
    cnt_retry = 0
    while cnt_retry < max_retry:
        try:
            response = requests.get(url, timeout=max_timeout)
            if response.status_code == requests.codes.ok:
                break
        except requests.exceptions.ReadTimeout as e:
            time.sleep(5)
            cnt_retry += 1
            if cnt_retry >= max_retry:
                raise e
    return response


def process_page(url):
    response = get_response(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def collect_next_urls(url, location=[]):
    soup = process_page(url)
    elements = soup.find_all(name="a")
    element = list(filter(lambda x: x.text=="сайт избирательной комиссии субъекта Российской Федерации", elements))
    if element and len(location) == 2:
        return {element[0].get("href"): location}
    elif element and len(location) == 1:
        return {url: location + location}
    
    elements = soup.find_all(name="a", attrs={"style": "text-decoration: none"})
    urls = {x.get("href"): location + [x.text] for x in elements}
    return urls


def collect_region_urls(url, location): 
    urls = {}
    # territorial urls
    urls_terr = collect_next_urls(url, location)
    # precinct urls
    for url_terr, location in urls_terr.items():
        urls_prec = collect_next_urls(url_terr, location)
        urls = {**urls, **urls_prec}
    return urls


def collect_dataframe_from_page(url, location):
    soup = process_page(url)
    tables_html = soup.find_all(name="table", attrs={"bgcolor": "#ffffff"})
    dfs = [pd.DataFrame(pd.read_html(str(x), flavor="bs4")[0]) for x in tables_html]
    df = pd.concat(dfs, axis=1, ignore_index=True)
    
    def process_dataframe(df):        
        df = df.iloc[:,1:].dropna(how="all", axis=(0,1))
        colnames = df.iloc[0,:]
        colnames[0:2] = ["metric", "value"]
        df.columns = colnames
        df.drop("value", axis=1, inplace=True)
        df = df.iloc[1:, :].applymap(lambda x: re.sub("\d+\.\d+%", "", x).strip() if "%" in x else x)        
        df = df.melt(id_vars="metric", value_name="value", var_name="PEC")
        return df
    
    df = process_dataframe(df)
    df["Region"], df["TEC"] = location
    df = df[["metric", "Region", "TEC", "PEC", "value"]]
    return df


def tqdm_parallel_map(fn, *iterables, **kwargs):
    with futures.ThreadPoolExecutor(max_workers=32) as executor:
        futures_list = [executor.submit(fn, *it) for it in zip(*iterables)]
        
        for f in tqdm_notebook(futures.as_completed(futures_list), total=len(futures_list), **kwargs):
            pass
    
    results = [f.result() for f in futures_list]
    return results


def get_data():
	main_url = "http://www.vybory.izbirkom.ru/region/region/izbirkom?action=show&root=1&tvd=100100084849066&vrn=100100084849062&region=0&global=1&sub_region=0&prver=0&pronetvd=null&type=227"

	# regional urls
	urls_reg = collect_next_urls(main_url)

	# parallel URL collection
	results = tqdm_parallel_map(collect_region_urls, urls_reg.keys(), urls_reg.values(), desc="URLs")

	# collected URLs
	urls = {}
	for res in results:
	    urls = {**urls, **res}
	
	 # parallel data collection from tables
	dfs = tqdm_parallel_map(collect_dataframe_from_page, urls.keys(), urls.values(), desc="Tables")
	data = pd.concat(dfs, axis=0, ignore_index=True)
	return data
