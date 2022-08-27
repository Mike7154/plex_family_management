# pylama:ignore=W0401,W0612

from plexapi.myplex import MyPlexAccount
# import time
# import json
from general_functions import *


# Connect to Plex
def plex_account(plex_email, plex_password):
    PLEXAPI_PLEXAPI_TIMEOUT = 200
    account = MyPlexAccount(plex_email, plex_password)
    return account


def plex_connect(plex_server, account):
    plex = account.resource(plex_server).connect()
    PLEXAPI_PLEXAPI_TIMEOUT = 200
    return plex


def session_duration(plex):  # get the duration of the longest item playing currently. It gets the full movie duration unfortunately
    sessions = plex.sessions
    durration = [0]
    for s in sessions:
        duration.append(s.duration)
    return max(duration)


def remLabels(movie, labels):
    mlabs = [i.tag for i in movie.labels]
    rlabs = [i for i in mlabs if i in labels]
    for rl in rlabs:
        print(movie.title + ' removing ' + rl)
        movie.removeLabel(rl).reload()


def remove_items_labels(items, labels):
    for i in items:
        remLabels(i, labels)


def add_items_labels(items, labels):
    for i in items:
        for label in labels:
            i.addLabel(label).reload()


def clear_labels(items, remove_labels, add_label=""):
    for i in items:
        labels = list_movie_age_labels(i, remove_labels)
        remLabels(i, labels)
        if add_label != "":
            i.addLabel(add_label)


def list_movie_age_labels(movie, age_labels):
    m_labels = [i.tag for i in movie.labels]
    return list(set(m_labels).intersection(age_labels))


def build_age_labels(age, gender="", gender_specific=False, age_label_prefix = "", age_label_suffix = "", gender_specific_txt = ["",""]):
    labels = []
    ages = range(1, age+1)
    for a in ages:
        a = age_label_prefix + str(a) + age_label_suffix
        labels.append(str(a))
        if gender_specific is True:
            if gender == "F" or gender == "both":
                labels.append(str(a)+gender_specific_txt[0])
            if gender == "M" or gender == "both":
                labels.append(str(a)+gender_specific_txt[1])
    return labels


def get_user_labels(user, days_early = 0, gender_specific = False, age_label_prefix = "", age_label_suffix = "", gender_specific_txt = ["",""]):
    if user.dob is None:
        if user.age is None:
            text = user.username + " does not have a DOB or age listed. Please enter it in settings if you want to approve age-apropriate content"
            print(text)
            update_log(text)
            return [user.username]
        else:
            age = user.age
    else:
        age = round(get_age(user.dob)-0.5+(days_early)/365)
    gender = user.gender
    if gender is None:
        gender_specific = False
    labels = [user.username]
    labels.extend(build_age_labels(age, gender, gender_specific, age_label_prefix, age_label_suffix, gender_specific_txt))
    return labels


def user_exists(username, account):
    account_users = account.users()
    user_list = [u.title for u in account_users]
    return username in user_list


def playlist_exists(playlist, library):
    playlists = library.playlists()
    pl_list = [p.title for p in playlists]
    return playlist in pl_list


def get_labeled_movies(library, labels):
    a_labels = labels
    labeled_movies = []
    for label in a_labels:
        labeled_movies = list(set(labeled_movies + library.search(label=label)))
    return labeled_movies


def get_unlabeled_movies(library, labels):
    labeled_movies = get_labeled_movies(library, labels)
    movies = difference(library.all(), labeled_movies)
    return movies


def movies_to_run(lib, movies_dict, update_freq=5):
    movies_to_skip = []
    for m in movies_dict:
        v = url_dict.get(m)
        mov = lib.getGuid(k)
        c_age = get_age(str_to_date(url_dict.get(k)))
        m_age = get_age(mov.originallyAvailableAt)
        if m_age/c_age > update_age_factor and s_age < update_freq:
            movies_to_skip.append(k)
    movies = [m for m in all_movies if m.guid in movies_to_skip]
    return difference(all_movies, movies)
