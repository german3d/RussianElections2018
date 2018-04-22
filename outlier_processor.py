import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import IsolationForest
from data_processor import get_clean_data
from config import data_dirname, data_fname_clean, data_fname_outliers, features_outliers


def get_outliers(**kwargs):
    if os.path.isfile(data_dirname + data_fname_outliers):
        with open(data_dirname + data_fname_outliers, "rb") as f:
            data_outliers = pickle.load(file=f)
    else:
        data = get_clean_data()
        features = ["filled_abs", "turnout_share", "stolen_share",]
        data_train = data["PEC"].loc[data["PEC"]["filled_abs"] > 100, features_outliers]\
        				.drop(["Город Байконур (Республика Казахстан)", "Территория за пределами РФ"], level="District")
        idxs_outliers = train_detector(data_train, **kwargs)
        total_putin = data["Total"]["Путин Владимир Владимирович (%)"].item()
        idxs_suspicious = (data_train["Путин Владимир Владимирович (%)"] > total_putin).values 
        locations = data_train[idxs_outliers & idxs_suspicious].index
        data_outliers = {"PEC": data["PEC"].loc[locations]} # dict for consistency with full data format
        with open(data_dirname + data_fname_outliers, "wb") as f:
            pickle.dump(obj=data_outliers, file=f)
    return data_outliers


def train_detector(data, **kwargs):
	model = IsolationForest(n_estimators=1000, random_state=13, **kwargs);
	model.fit(data);
	pred = model.predict(data);
	idxs = np.array([True if x==-1 else False for x in pred])
	return idxs
