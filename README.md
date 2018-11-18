## Presidential Election in Russia (18.03.2018)

This project is aimed to collect, visualize and find anomalies in presidential election data.

Binder link to interactive dashboard: [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/german3d/RussianElections2018/master?filepath=dashboard.ipynb)


#### Main parts:
1. Web scraping [official website](http://www.vybory.izbirkom.ru/region/izbirkom) of the Central Election Commission:
- `requests`
- `beautifulsoup` 
- `concurrent`

2. Data visualization: 
- `plotly` 
- `seaborn` 
- `cufflinks` 
- `ipywidgets`

3. Anomaly detection: 
- `scikit-learn` (Isolation Forest)
