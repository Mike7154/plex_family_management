# pylama:ignore=E741,W0401

import csmedia
import plex_functions
from settings import *
from general_functions import *
from datetime import datetime
from datetime import timedelta
now = datetime.now()
plex = plex_functions.plex_connect()
print(plex)


##################################################
# from importlib import reload
# reload(csmedia)
# reload(plex_functions)
# library = "Movies"
# movie = all_movies[388]
####################################################################################################
# Approve labels
# If setting file allows. this will allow labels that match the child's age.
# Update the usernames and birthdays in the settings
account = plex_functions.plex_account()
for u in users['users']:
    labels = plex_functions.get_user_labels(u)
    username = u['username']
    print(username)
    if plex_functions.user_exists(username) is False:
        account.createHomeUser(username, plex, libraries)
        account = plex_functions.plex_account()
    user = account.user(username)
    account.updateFriend(user, plex, filterMovies={'label': labels}, filterTelevision={'label': labels})

###############################################################
####################################################################################################
for library in libraries:
    update_log("Starting Library "+library)
    movies = plex.library.section(library)
    library_type = movies.type
    if library_type not in library_types:
        update_log("Skipping library " + library + " Type " + library_type)
        next
    all_movies = movies.all()

    ####################################################################################################
    # COMMON SENSE MEDIA
    # IF the settings.ini file sets to run this, it will get movie information for parents from Common Sense Media
    # and add it to the movie summary. This includes information like language, nudity, and diverse representation
    # as well as recommended ages
    #####################################################################################################
    # Load bad_urls
    movie_dict = load_dict(movie_dict_file)
    movies_to_run = all_movies
    c = 0
    if run_common_sense_media is True and CLEAN_LIBRARY is False:
        for movie in movies_to_run:
            # print(movie.title)
            if csmedia.should_i_get_csm(movie) is True:
                if movie.guid not in movie_dict:
                    movie_dict.update({movie.guid: {'verified': False}})
                m_dict = movie_dict.get(movie.guid)
                m_dict = csmedia.CSM_get(movie, m_dict, movies, library_type)
                csm = m_dict.get('cs_summary')
                if csm is not None:
                    s = csmedia.remove_csm(movie)
                    s = s + "\n" + csm
                    movie.editSummary(s)
                    print("Edited Summary for " + movie.title)
                    c = c+1
                else:
                    print(movie.title + ": Missing from Common Sense Media")
                movie_dict.update({movie.guid: m_dict})
            # else:
                # print("Should skip. Common sense media already updated or not required")
    write_dict(movie_dict_file, movie_dict)
    update_log("Updated Summaries for " + str(c) + " movies")
    ###############################################################
    # If the settings.py file says to, this will add a label to each movie with a missing label. The label will match
    # the recommended age from common sense media
    c = 0
    if approve_common_sense_media_ages is True and CLEAN_LIBRARY is False:
        unlabeled_movies = plex_functions.get_unlabeled_movies(movies)
        movies_to_run = unlabeled_movies
        for movie in movies_to_run:
            m_dict = movie_dict.get(movie.guid)
            age = m_dict.get('cs_age')
            if age is not None:
                age = str(age)
                movie.addLabel(age_label_prefix + age + age_label_suffix).reload()
                print("added label "+age)
                c = c + 1
            else:
                print("skipping length 0")
                if use_unlabeled_label is True:
                    movie.addLabel('Unlabeled').reload()
    else:
        print("Skipping common sense media labels")
    update_log("Updated age labels for " + str(c) + " movies")
    # END COMMON SENSE MEDIA SECTION
    ###############################################################
    ####################################################################################################

    # Update movie sharing from Playlists
    # Movies added to the playlist will be shared with the user
    if run_playlist_approve is True and CLEAN_LIBRARY is False and library_type == 'movies':
        # Unapprove playlist
        if unapprove_playlist != "":
            if plex_functions.playlist_exists(unapprove_playlist, movies) is False:
                i = [all_movies[1]]
                pl = movies.createPlaylist(unapprove_playlist, i)
                pl.removeItems(i)
            pl = movies.playlist(unapprove_playlist)
            items = pl.items()
            user_labels = [u.title for u in account.users()]
            plex_functions.clear_labels(items, unapprove_label, "", user_labels)
            pl = movies.playlist(unapprove_playlist)
            items = pl.items()
            pl.removeItems(items)
        else:
            print("No unapprove playlist entered. Skipping")
        # ------------------------------------------------------------------------
        # Approve playlist
        if approve_playlist != "":
            if plex_functions.playlist_exists(approve_playlist, movies) is False:
                i = [all_movies[1]]
                pl = movies.createPlaylist(approve_playlist, i)
                pl.removeItems(i)
            pl = movies.playlist(approve_playlist)
            items = pl.items()
            plex_functions.add_items_labels(items, [age_label_prefix + "1" + age_label_suffix])
            plex_functions.remove_items_labels(items, [unapprove_label])
            pl = movies.playlist(approve_playlist)
            items = pl.items()
            pl.removeItems(items)
        else:
            print("No unapprove playlist entered. Skipping")
        # ------------------------------------------------------------------------

        # User Playlists
        for u in users['users']:
            playlist = u['playlist']
            username = u['username']
            print("approving " + playlist + " movies for " + username)

            bday = plex_functions.str_to_date(u['dob'])
            age = round(plex_functions.get_age(bday)-0.49999)
            if offset_playlist_approve < 0:
                labels = [username]
            else:
                age = age + offset_playlist_approve
                age = age_label_prefix + str(age)+age_label_suffix
                labels = [username, age]
            if playlist != "":
                if plex_functions.playlist_exists(playlist, movies) is False:
                    i = [all_movies[1]]
                    pl = movies.createPlaylist(playlist, i)
                    pl.removeItems(i)
                pl = movies.playlist(playlist)
                items = pl.items()
                plex_functions.add_items_labels(items, labels)
                plex_functions.remove_items_labels(items, [unapprove_label])
                pl = movies.playlist(playlist)
                items = pl.items()
                pl.removeItems(items)
            else:
                print("No user playlist entered. Skipping")

    ############################################################
    # Remove unlabeled tag for any movie with age labels
    labeled_movies = plex_functions.get_labeled_movies(movies)
    movie_list = list(set(movies.search(label="Unlabeled")).intersection(labeled_movies))
    for movie in movie_list:
        print(movie.title)
        movie.removeLabel('Unlabeled')

    if use_unlabeled_label is True and CLEAN_LIBRARY is False:
        unlabeled_movies = difference(all_movies, labeled_movies)
        for movie in unlabeled_movies:
            print('Adding unlabeled to '+movie.title)
            movie.addLabel('Unlabeled')
    ############################################################
    ####################################################################################################
    # Clean Library - Remove common sense labels and Summaries
    if CLEAN_LIBRARY is True:
        for movie in all_movies:
            if "[Common Sense Media]" in movie.summary:
                print("cleaning " + movie.title)
                s = csmedia.remove_csm(movie)
                movie.editSummary(s, locked=False)
                for label in plex_functions.list_movie_age_labels(movie):
                    movie.removeLabel(label).reload()
        update_log("Cleaned Libraries, it's a good idea to refresh all metadata")

    ####################################################################################################
    # Add and remove collection labels
    last_run = movie_dict.get("Collection")
    last_run = last_run.get('updated')
    if last_run is None:
        movie_dict.update({'Collection': {"updated": "1900-01-01"}})
        last_run = now - deltatime(days=10)
    else:
        last_run = str_to_date(last_run)

    if run_col_labels is True and now - timedelta(days=update_collection_sync_freq) >= last_run:
        collections = movies.search(libtype='collection')
        col = collections[20]
        for col in collections:
            # cont = False
            print(col.title)
            labels = col.labels
            items = col.items()
            i_labels = []
            # for i in items:
            #    if i.updatedAt + timedelta(days=2) > plex_functions.str_to_date(str(movie_dict.get('Collections'))):
            #        cont = True
            #        break
            # if cont is False:
            #    continue
            for i in items:
                i_labels.extend([l.tag for l in i.labels])
            i_labels = list(set(i_labels))
            c_labels = [l.tag for l in labels]
            labels_to_add = difference(i_labels, c_labels)
            labels_to_remove = difference(c_labels, i_labels)

            for l in labels_to_remove:
                print('removing ' + l + ' from ' + col.title)
                col.removeLabel(l).reload()

            for l in labels_to_add:
                print('adding  '+l+' to ' + col.title)
                col.addLabel(l).reload()
        movie_dict.update({"Collection": {"updated": now.strftime('%Y-%m-%d')}})
    else:
        update_log("Skipping collection label updates (check settings for freq)")
    write_dict(movie_dict_file, movie_dict)
    # save URL dictionary of movies that I coulnd't find on CSM
write_dict(movie_dict_file, movie_dict)


print("-----------------------------------------------------------------------------")
print("END OF SCRIPT.")
update_log("RUN COMPLETE")
##################################################################
