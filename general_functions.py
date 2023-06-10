import json
from datetime import datetime
import re
import urllib.parse
import ruamel.yaml
# -------------------------------------------------------------------------


class User:
    def __init__(self, username, gender, dob, age, playlist):
        self.username = username
        self.gender = gender
        self.dob = dob
        self.age = age
        self.playlist = playlist
# -------------------------------------------------------------------------

def combine_unique(list1, list2):
    list = list1
    list.extend(list2)
    newlist = []
    for x in list:
        if x not in newlist:
            newlist.append(x)
    return newlist

def build_filter(text, labels):
    if text == '':
        filter = {'label': labels}
    else:
        text = urllib.parse.unquote(text)
        text = re.split(r'[&|]', text)
        filter = {}
        i = text[0]
        for i in text:
            pair = i.split("=")
            filter.update({pair[0]:pair[1].split(",")})
        label_filter = filter.get("label")
        if label_filter is None:
            label_filter = labels
        else:
            label_filter = combine_unique(label_filter, labels)
        filter.update({"label":label_filter})
    return filter

def str_to_date(str):
    return datetime.strptime(str, '%Y-%m-%d').date()


def get_age(date):
    age = datetime.now().date()-date
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
    print(text)
    file = "logs.txt"
    timestr = now.strftime('%m/%d/%Y %H:%M:%S')
    log_text = timestr + " : " + text
    f = open(file, "a")
    f.write(log_text+'\n')
    f.close()

def load_setting(section, setting, settings_file = "settings.yml"):
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    with open(settings_file) as fp:
        data = yaml.load(fp)
    return data[section][setting]