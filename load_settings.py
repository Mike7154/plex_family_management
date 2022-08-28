import plex_functions
import sys
import ruamel.yaml
import cryptocode
import shutil
import os
from general_functions import *

# Variables - don't change these
csm_URLs = {
    'base': 'https://www.commonsensemedia.org',
    'movie': "https://www.commonsensemedia.org/search/category/movie/",
    'tv': 'https://www.commonsensemedia.org/search/category/tv/',
    'movie_reviews': '/movie-reviews/',
    'tv_reviews': '/tv-reviews/'}
library_types = ['movie', 'show']
movie_dict_file = "movie_data.json"
settings = "settings.yml"
yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True
if os.path.isfile(settings) == False:
    shutil.copy("settings_blank.yml", settings)

with open(settings) as fp:
    data = yaml.load(fp)


#Update missing settings
if data['Login']['plex_email'] is None:
    data['Login']['plex_email'] = input("Please type your plex email: ")
if data['Login']['plex_password'] is not None:
    data['Misc']['hash'] = cryptocode.encrypt(data['Login']['plex_password'], data['Login']['plex_email'])
    data['Login']['plex_password'] = None
if data['Misc']['hash'] is None:
    password = input("Please type your plex password (it will only be stored locally with basic encryption): ")
    data['Misc']['hash'] = cryptocode.encrypt(password, data['Login']['plex_email'])
    data['Login']['plex_password'] = None

pe = data['Login']['plex_email']
pp = cryptocode.decrypt(data['Misc']['hash'], pe)
try:
    account = plex_functions.plex_account(pe, pp)
except:
    text = "Could not login to your plex server, please check the plex email and password in settings.yml and try again"
    print(text)
    update_log(text)
    data['Login']['plex_password'] = pp
    data['Misc']['hash'] = None
    with open(settings, "w") as f:
        yaml.dump(data,f)
    sys.exit()

if data['Login']['plex_server'] is None:
    data['Login']['plex_server'] = input("What is the name of the plex server you want to connect to?: ")

now = datetime.now().date()
plex = plex_functions.plex_connect(data['Login']['plex_server'], account)
PLEXAPI_PLEXAPI_TIMEOUT=3800


if data['Login']['libraries'] is None:
    libraries = []
    for lib in plex.library.sections():
        if lib.type in library_types:
            text = input("Do you want this script to run for the library '" + lib.title + "'? (y/n): ")
            if text == 'y':
                libraries.append(lib.title)
    data['Login']['libraries'] = libraries
print(plex)
libraries = []
libraries.extend(data['Login']['libraries'])

def input_user_data(u):
    user = {}
    if input("Do you want to manage the user '"+ u.title +"'? (y/n): ") == 'y':
        user['username'] = u.title
        user['gender'] = input("What is the gender of '"+ u.title +"'? (M/F/both): ")
        birthday = input("What is the birthdate of '"+ u.title +"'? ENTER to skip (YYYY-MM-DD): ")
        if birthday == '':
            age = input("Do you want an age appropriate cutoff for the account '"+ u.title +"'? (ie. 13): ")
            if age != '':
                user['age'] = int(age)
        else:
            user['dob'] = str_to_date(birthday)
        playlist = input("What is the name of the playlist to approve movies for the account '"+ u.title +"'? ENTER to skip: ")
        if playlist != '':
            user['playlist'] = playlist
        return user
    else:
        return None

if data['Users'] is None:
    users = []
    u = account.users()[1]
    for u in account.users():
        user = input_user_data(u)
        if user is not None:
            users.append(user)
    data['Users'] = users

prompt = data['Run'].get('prompt_user_input')
if prompt is None:
    data['Run'].update({'prompt_user_input':False})
elif prompt is True:
    users = data['Users']
    for u in account.users():
        if u.title not in [i['username'] for i in users]:
            user = input_user_data(u)
            if user is not None:
                users.append(user)
    data['Users'] = users
    data['Run'].update({'prompt_user_input':False})

with open(settings, "w") as f:
    yaml.dump(data,f)

users = []
for user in data['Users']:
    u = User(user.get('username'), user.get('gender'), user.get('dob'), user.get('age'), user.get('playlist'))
    users.append(u)


def cblank_text(text):
    if text is None:
        text = ""
    return text

# [RUN]
# ------------------------------------------------------------------------
run_common_sense_media = data['Run']['run_common_sense_media']
approve_common_sense_media_ages =  data['Run']['approve_common_sense_media_ages']
run_playlist_approve = data['Run']['run_playlist_approve']
run_col_labels = data['Run']['run_col_labels']
run_auto_approve = data['Run']['run_auto_approve']
CLEAN_LIBRARY = data['Run']['CLEAN_LIBRARY']

#Labels:
unapprove_playlist = cblank_text(data['Labels'].get('unapprove_playlist'))
approve_playlist = cblank_text(data['Labels'].get('approve_playlist'))
unapprove_label = cblank_text(data['Labels'].get('unapprove_label'))
use_unlabeled_label = cblank_text(data['Labels'].get('use_unlabeled_label'))
age_label_prefix = cblank_text(data['Labels'].get('age_label_prefix'))
age_label_suffix = cblank_text(data['Labels'].get('age_label_suffix'))
gender_specific = cblank_text(data['Labels'].get('gender_specific'))
gender_specific_txt = cblank_text(data['Labels'].get('gender_specific_txt'))

#Misc
days_early = data['Misc']['days_early']
offset_playlist_approve = data['Misc']['offset_playlist_approve']
update_collection_sync_freq = data['Misc']['update_collection_sync_freq']
ignore_prefix = []
if data['Misc'].get('ignore_prefix') is not None:
    ignore_prefix.extend(data['Misc'].get('ignore_prefix'))



#CSM:
parents_review = data['CSM']['parents_review']
extra_label = cblank_text(data['CSM'].get('extra_label'))
update_old_summaries = data['CSM']['update_old_summaries']
update_age_factor = data['CSM']['update_age_factor']
