## Presidential Elections in Russia (18.03.2018)

This project is aimed to collect, visualize and find anomalies in official election results data.

Binder link to interactive dashboard: [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/german3d/RussianElections2018/master)


#### Main parts:
1. Web scraping [official website](http://www.vybory.izbirkom.ru/region/izbirkom) of the Central Election Commission of the Russian Federation: *requests + BeatifulSoup + concurrent*.
2. Data visualization: *plotly + seaborn + cufflinks + ipywidgets*.
3. Anomaly detection: *scikit-learn*.