data_dirname = "./data/"
data_fname_raw = "raw_data.gz"
data_fname_clean = "clean_data.pcl"
district_fname = "russian_federal_districts.json"

main_url = "http://www.vybory.izbirkom.ru/region/region/izbirkom?action=show&root=1&tvd=100100084849066&vrn=100100084849062&region=0&global=1&sub_region=0&prver=0&pronetvd=null&type=227"

candidates = ["Бабурин Сергей Николаевич",
              "Грудинин Павел Николаевич",
              "Жириновский Владимир Вольфович",
              "Путин Владимир Владимирович",
              "Собчак Ксения Анатольевна",
              "Сурайкин Максим Александрович",
              "Титов Борис Юрьевич",
              "Явлинский Григорий Алексеевич"]


hierarchy = ["Total", "District", "Region", "TEC", "PEC"]


metrics_to_russian = {#"candidate":       "Кандидат",
                      #"votes_abs":       "Голосов за канд-та (абс)",
                      #"votes_share":     "Голосов за канд-та (%)",
                      "filled_abs":      "Число заполненных бюллетеней",
                      "distributed_abs": "Число выданных бюллетеней",
                      "listed_abs":     "Число избирателей в списках",
                      "turnout_share":   "Явка (%)",
                      "spoiled_abs":     "Кол-во испорченных бюллетеней (абс)",
                      "spoiled_share":   "Кол-во испорченных бюллетеней (%)",
                      "stolen_abs":      "Кол-во унесенных бюллетеней (абс)",
                      "stolen_share":    "Кол-во унесенных бюллетеней (%)",
                     }

metrics_to_russian = {**metrics_to_russian, **{c+" (абс)": c+" (абс)" for c in candidates}, **{c+" (%)": c+" (%)" for c in candidates} }
