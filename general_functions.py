import json
from datetime import datetime


def str_to_date(str):
    return datetime.strptime(str, '%Y-%m-%d')


def get_age(date):
    age = datetime.now()-date
    age = age.total_seconds()
    age = age/3600
    age = age/24
    age = age/365
    return age


def difference(list1, list2):
    list_dif = [i for i in list1 if i not in list2]
    return list_dif


def load_dict(file):
    f = open(file)
    url_dict = json.load(f)
    f.close()
    return url_dict


def write_dict(file, dict):
    with open(file, "w") as convert_file:
        convert_file.write(json.dumps(dict))


def update_log(text):
    now = datetime.now()
    file = "logs.txt"
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    log_text = timestr + " : " + text
    f = open(file, "a")
    f.write(log_text+'\n')
    f.close()
