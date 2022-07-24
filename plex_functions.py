from plexapi.myplex import MyPlexAccount
from datetime import datetime
import time
import json
from settings import *


#Connect to Plex
def plex_account():
    PLEXAPI_PLEXAPI_TIMEOUT=200
    account = MyPlexAccount(plex_email,plex_password)
    return account

def plex_connect(account = plex_account()):
    plex = account.resource(plex_server).connect()
    PLEXAPI_PLEXAPI_TIMEOUT=200
    return plex

def session_duration(plex): #get the duration of the longest item playing currently. It gets the full movie duration unfortunately
    sessions = plex.sessions
    durration=[0]
    for s in sessions:
        duration.append(s.duration)
    return max(duration)

def remLabels(movie, labels):
    mlabs = [i.tag for i in movie.labels]
    rlabs = [i for i in mlabs if i in labels]
    for rl in rlabs:
        print(movie.title + ' removing ' + rl)
        movie.removeLabel(rl).reload()

def add_items_labels(items, labels):
    for i in items:
        for l in labels:
            i.addLabel(l).reload()

def clear_labels(items, add_label = "", ignore_label ="", remove_labels = [] ):
    for i in items:
        labels = list_movie_age_labels(i)
        labels.extend(remove_labels)
        if ignore_label in labels:
            labels.remove(ignore_label)
        remLabels(i,labels)
        if add_label !="":
            i.addLabel(add_label)

def list_movie_age_labels(movie):
    m_labels = [i.tag for i in movie.labels]
    a_labels = [unapprove_label]
    a_labels.extend(build_age_labels(25, gender = "both", gender_specific = True))
    return list(set(m_labels).intersection(a_labels))




def str_to_date(str):
    return datetime.strptime(str, '%Y-%m-%d')

def get_age(date):
    age = datetime.now()-date
    age = age.total_seconds()
    age = age/3600
    age = age/24
    age = age/365
    return age

def build_age_labels(age, gender = "", gender_specific = False):
    labels = []
    ages = range(1,age+1)
    for a in ages:
        a = str(a) + age_label_append
        labels.append(str(a))
        if gender_specific == True:
            if gender == "F" or gender =="both":
                labels.append(str(a)+gender_specific_txt[0])
            if gender =="M" or gender =="both":
                labels.append(str(a)+gender_specific_txt[1])
    return labels

def get_user_labels(user):
        username = user['username']
        gender = user['gender']
        bday = str_to_date(user['dob'])
        age = round(get_age(bday)-0.49999+(days_early)/365)
        labels = [username]
        labels.extend(build_age_labels(age, gender, gender_specific))
        return labels

def user_exists(username, account = plex_account()):
    account_users = account.users()
    user_list = [u.title for u in account_users]
    return username in user_list

def playlist_exists(playlist, library):
    playlists = library.playlists()
    pl_list = [p.title for p in playlists]
    return playlist in pl_list

def difference (list1, list2):
   list_dif = [i for i in list1 if i not in list2]
   return list_dif

def get_labeled_movies(movies):
    a_labels = [unapprove_label]
    a_labels.extend(build_age_labels(25, gender = "both", gender_specific = True))
    labeled_movies = []
    for l in a_labels:
        labeled_movies = list(set(labeled_movies + movies.search(label = l)))
    return labeled_movies

def get_unlabeled_movies(movies):
    labeled_movies = get_labeled_movies(movies)
    movies = difference(movies.all(),labeled_movies)
    return movies

def load_dict(file):
    f = open(file)
    url_dict = json.load(f)
    f.close()
    return url_dict

def write_dict(file, dict):
    with open(file,"w") as convert_file:
        convert_file.write(json.dumps(dict))

def movies_to_run(all_movies, url_dict, update_freq = 0.5):
    movies_to_skip = []
    for k in url_dict:
        date = str_to_date(url_dict.get(k))
        if get_age(date) < update_freq:
            movies_to_skip.append(k)
    movies = [m for m in all_movies if m.title in movies_to_skip]
    return difference(all_movies, movies)
