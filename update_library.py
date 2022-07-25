import csmedia
import plex_functions
from settings import *
from datetime import datetime
now = datetime.now()
plex = plex_functions.plex_connect()
print(plex)
movies = plex.library.section(movie_library)
all_movies = movies.all()
####################################################################################################
#COMMON SENSE MEDIA
#IF the settings.ini file sets to run this, it will get movie information for parents from Common Sense Media
#and add it to the movie summary. This includes information like language, nudity, and diverse representation
#as well as recommended ages
#####################################################################################################
#Load bad_urls
url_dict = plex_functions.load_dict(bad_urls_json)
movies_to_run = plex_functions.movies_to_run(all_movies, url_dict)

if run_common_sense_media==True:
    for movie in movies_to_run:
        print(movie.title)
        if csmedia.should_i_get_csm(movie) == True:
            csm = csmedia.CSM_get(movie.title, str(movie.year))
            if len(csm) > 0:
                s = csmedia.remove_csm(movie)
                s = s + "\n"+ csm
                movie.editSummary(s)
                print("Edited Summary for " + movie.title)
            else:
                print("Couldn't find "+movie.title+" in common sense media, skipping")
                url_dict.update({movie.title:now.strftime('%Y-%m-%d')})
        else:
            print("Should skip. Common sense media already updated or not required")
###############################################################
#If the settings.py file says to, this will add a label to each movie with a missing label. The label will match
#the recommended age from common sense media
if approve_common_sense_media_ages==True:
    unlabeled_movies = plex_functions.get_unlabeled_movies(movies)
    movies_to_run = plex_functions.movies_to_run(all_movies, url_dict)
    for movie in list(set(unlabeled_movies).intersection(movies_to_run)):
        print(movie.title)
        age = csmedia.CSM_approve_age(movie.title, str(movie.year))
        if len(age)>0:
            movie.addLabel(age + age_label_append).reload()
            print("added label "+age)
        else:
            print("skipping length 0")
            if use_unlabeled_label == True:
                movie.addLabel('Unlabeled').reload()
    print("Skipping common sense media labels")
#END COMMON SENSE MEDIA SECTION
###############################################################
####################################################################################################

####################################################################################################
#Approve labels
#If setting file allows. this will allow labels that match the child's age.
#Update the usernames and birthdays in the settings
account = plex_functions.plex_account()
u = users['users'][1]
for u in users['users']:
    labels = plex_functions.get_user_labels(u)
    username = u['username']
    print(username)
    if plex_functions.user_exists(username) == False:
        account.createHomeUser(username, plex, [movie_library])
        account = plex_functions.plex_account()
    user = account.user(username)
    account.updateFriend(user,plex,filterMovies = {'label':labels}, filterTelevision = {'label':labels})


###############################################################
#Update movie sharing from Playlists
#Movies added to the playlist will be shared with the user
if run_playlist_approve == True:
    #Unapprove playlist
    if unapprove_playlist != "":
        if plex_functions.playlist_exists(unapprove_playlist, movies) == False:
            i = [all_movies[1]]
            pl = movies.createPlaylist(unapprove_playlist, i)
            pl.removeItems(i)
        pl = movies.playlist(unapprove_playlist)
        items = pl.items()
        user_labels = [u.title for u in account.users()]
        plex_functions.clear_labels(items, unapprove_label,"", user_labels)
        pl = movies.playlist(unapprove_playlist)
        items = pl.items()
        pl.removeItems(items)
    else:
        print("No unapprove playlist entered. Skipping")
    #------------------------------------------------------------------------
    #Approve playlist
    if approve_playlist != "":
        if plex_functions.playlist_exists(approve_playlist, movies) == False:
            i = [all_movies [1]]
            pl = movies.createPlaylist(approve_playlist, i)
            pl.removeItems(i)
        pl = movies.playlist(approve_playlist)
        items = pl.items()
        plex_functions.add_items_labels(items, ["1" + age_label_append])
        plex_functions.remove_items_labels(items,[unapprove_label])
        pl = movies.playlist(approve_playlist)
        items = pl.items()
        pl.removeItems(items)
    else:
        print("No unapprove playlist entered. Skipping")
    #------------------------------------------------------------------------
    #User Playlists
    for u in users['users']:
        playlist = u['playlist']
        username = u['username']
        print("approving "+playlist+" movies for "+ username)

        bday = plex_functions.str_to_date(u['dob'])
        age = round(plex_functions.get_age(bday)-0.49999)
        if offset_playlist_approve <0:
            labels = [username]
        else:
            age = age + offset_playlist_approve
            age = str(age)+age_label_append
            labels = [username, age]
        if playlist != "":
            if plex_functions.playlist_exists(playlist, movies) == False:
                i = [all_movies [1]]
                pl = movies.createPlaylist(playlist, i)
                pl.removeItems(i)
            pl = movies.playlist(playlist)
            items = pl.items()
            plex_functions.add_items_labels(items, labels)
            plex_functions.remove_items_labels(items,[unapprove_label])
            pl = movies.playlist(playlist)
            items = pl.items()
            pl.removeItems(items)
        else:
            print("No user playlist entered. Skipping")

############################################################
#Remove unlabeled tag for any movie with age labels
labeled_movies = plex_functions.get_labeled_movies(movies)
movie_list = list(set(movies.search(label="Unlabeled")).intersection(labeled_movies))
for movie in movie_list:
    print(movie.title)
    movie.removeLabel('Unlabeled').reload()

unlabeled_movies = plex_functions.difference(all_movies,labeled_movies)
for movie in unlabeled_movies:
    print('Adding unlabeled to '+movie.title)
    movie.addLabel('Unlabeled').reload
############################################################
#Add and remove collection labels
def difference (list1, list2):
   list_dif = [i for i in list1 if i not in list2]
   return list_dif

if run_col_labels == True:
    collections = movies.search(libtype='collection')
    for col in collections:
        #cont = False
        print(col.title)
        labels = col.labels
        items = col.items()
        i_labels = []
        #for i in items:
        #    if i.updatedAt > plex_functions.str_to_date(str(url_dict.get('Collections'))):
        #        cont = True
        #        break
        #if cont == False:
        #    continue
        for i in items:
            i_labels.extend([l.tag for l in i.labels])
        i_labels = list(set(i_labels))
        c_labels = [l.tag for l in labels]
        labels_to_add = plex_functions.difference(i_labels,c_labels)
        labels_to_remove = plex_functions.difference(c_labels,i_labels)

        for l in labels_to_remove:
            print('removing '+l+' from '+ col.title)
            col.removeLabel(l).reload()

        for l in labels_to_add:
            print('adding  '+l+' to ' +col.title)
            col.addLabel(l).reload()
    url_dict.update({"Collections":now.strftime('%Y-%m-%d')})

#save URL dictionary of movies that I coulnd't find on CSM
plex_functions.write_dict(bad_urls_json, url_dict)
def write_dict(file, dict):
    with open(file,"w") as convert_file:
        convert_file.write(json.dumps(dict))


##################################################################
