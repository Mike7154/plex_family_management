# pylama:ignore=W0401
import csmedia
from general_functions import *
from datetime import datetime
from datetime import timedelta
from load_settings import *


##################################################
# from importlib import reload
# reload(csmedia)
# reload(plex_functions)
# library = "Movies"
# movie = all_movies[388]
age_labels = [unapprove_label]
age_labels.extend(plex_functions.build_age_labels(25, gender="both", gender_specific = gender_specific, age_label_prefix = age_label_prefix, age_label_suffix = age_label_suffix, gender_specific_txt = gender_specific_txt))
####################################################################################################
# Approve labels
# If setting file allows. this will allow labels that match the child's age.
# Update the usernames and birthdays in the settings


for u in users:
    labels = plex_functions.get_user_labels(u, days_early, gender_specific, age_label_prefix, age_label_suffix, gender_specific_txt)
    username = u.username
    print(username)
    if plex_functions.user_exists(username, account) is False:
        account.createHomeUser(username, plex, libraries)
        account = plex_functions.plex_account(pe, pp)
    user = account.user(username)
    text = user.filterMovies
    m_filter = build_filter(user.filterMovies, labels)
    t_filter = build_filter(user.filterTelevision, labels)
    account.updateFriend(user, plex, filterMovies=m_filter, filterTelevision=t_filter)

###############################################################
#library = libraries[0]
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
            if csmedia.should_i_get_csm(movie, update_old_summaries, update_age_factor) is True:
                if movie.guid not in movie_dict:
                    movie_dict.update({movie.guid: {'verified': False}})
                m_dict = movie_dict.get(movie.guid)
                m_dict = csmedia.CSM_get(movie, m_dict, movies, library_type, csm_URLs, update_age_factor, library_types, parents_review)
                csm = m_dict.get('cs_summary')
                if csm is not None:
                    s = csmedia.remove_csm(movie)
                    s = s + "\n" + csm
                    s = csmedia.restrip(s, "\n\n", "\n")
                    movie.editSummary(s)
                    print("Edited Summary for " + movie.title)
                    c = c+1
                else:
                    print(movie.title + ": Missing from Common Sense Media")
                movie_dict.update({movie.guid: m_dict})
                write_dict(movie_dict_file, movie_dict)
            # else:
                # print("Should skip. Common sense media already updated or not required")
    write_dict(movie_dict_file, movie_dict)
    update_log("Updated Summaries for " + str(c) + " movies")
    ###############################################################
    # If the settings.py file says to, this will add a label to each movie with a missing label. The label will match
    # the recommended age from common sense media
    c = 0
    if approve_common_sense_media_ages is True and CLEAN_LIBRARY is False:
        labs_to_check = age_labels
        unlabeled_movies = plex_functions.get_unlabeled_movies(movies, labs_to_check)
        movies_to_run = unlabeled_movies
        print("there are " + str(len(movies_to_run)) + " Unlabeled moves that I will search for common sense media ages")
        for movie in movies_to_run:
            if c % 15 == 0:
                write_dict(movie_dict_file, movie_dict)
                print("saving movie data")
            m_dict = movie_dict.get(movie.guid)
            if m_dict is None:
                movie_dict.update({movie.guid: {'verified': False}})
                m_dict = movie_dict.get(movie.guid)
                m_dict = csmedia.CSM_get(movie, m_dict, movies, library_type, csm_URLs, update_age_factor, library_types, parents_review)
                movie_dict.update({movie.guid: m_dict})
            age = m_dict.get('cs_age')
            if age is not None:
                age = str(age)
                movie.addLabel(age_label_prefix + age + age_label_suffix).reload()
                if extra_label != "":
                    movie.addLabel(extra_label)
                print("added label " + age + " for " + movie.title)
                c = c + 1
            else:
                print("skipping length 0 "+ movie.title)
                if use_unlabeled_label is True:
                    movie.addLabel('Unlabeled').reload()
        update_log("Updated age labels for " + str(c) + " movies")
        write_dict(movie_dict_file, movie_dict)
    else:
        print("Skipping common sense media labels")
    # END COMMON SENSE MEDIA SECTION
    ###############################################################
    ####################################################################################################

    # Update movie sharing from Playlists
    # Movies added to the playlist will be shared with the user
    if run_playlist_approve is True and CLEAN_LIBRARY is False and library_type == 'movie':
        # Unapprove playlist
        if unapprove_playlist != "":
            if plex_functions.playlist_exists(unapprove_playlist, movies) is False:
                i = [all_movies[1]]
                pl = movies.createPlaylist(unapprove_playlist, i)
                pl.removeItems(i)
            pl = movies.playlist(unapprove_playlist)
            items = pl.items()
            user_labels = [u.username for u in users]
            labs_to_check = user_labels
            labs_to_check.extend(age_labels)
            plex_functions.clear_labels(items, labs_to_check, unapprove_label)
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
        for u in users:
            playlist = cblank_text(u.playlist)
            username = u.username

            bday = u.dob
            if bday is None:
                age = u.age
            else:
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
                print("approving " + str(len(items)) + " items in " + playlist + " movies for " + username)
                plex_functions.add_items_labels(items, labels)
                plex_functions.remove_items_labels(items, [unapprove_label])
                pl = movies.playlist(playlist)
                items = pl.items()
                pl.removeItems(items)
            else:
                print("No user playlist entered. Skipping " + username)

    ############################################################
    # Remove unlabeled tag for any movie with age labels
    labs_to_check = age_labels
    labeled_movies = plex_functions.get_labeled_movies(movies, labs_to_check)
    movie_list = list(set(movies.search(label="Unlabeled")).intersection(labeled_movies))
    for movie in movie_list:
        print(movie.title)
        movie.removeLabel('Unlabeled').reload()

    if use_unlabeled_label is True and CLEAN_LIBRARY is False:
        unlabeled_movies = difference(all_movies, labeled_movies)
        for movie in unlabeled_movies:
            print('Adding unlabeled to '+movie.title)
            movie.addLabel('Unlabeled')
    ############################################################
    ####################################################################################################
    # Clean Library - Remove common sense labels and Summaries
    if CLEAN_LIBRARY is True:
        labels_to_clean = age_labels
        labeled_movies = plex_functions.get_labeled_movies(movies, labels_to_clean)
        plex_functions.clear_labels(labeled_movies, labels_to_clean)
        for movie in all_movies:
            if "[Common Sense Media]" in movie.summary:
                print("cleaning " + movie.title)
                s = csmedia.remove_csm(movie)
                movie.editSummary(s, locked=False)
                for label in plex_functions.list_movie_age_labels(movie, labels_to_clean):
                    movie.removeLabel(label).reload()
        update_log("Cleaned Libraries, it's a good idea to refresh all metadata")

    ####################################################################################################
    # Add and remove collection labels
    if run_col_labels is True:
        collections = movies.search(libtype='collection')
        col = collections[20]
        c = 0
        labs_to_sync = [u.title for u in account.users()]
        labs_to_sync.extend(age_labels)
        for col in collections:
            # cont = False
            print(col.title)
            if col.titleSort.startswith(tuple(ignore_prefix)) and ignore:
                print("--skipping due to collection prefix rule")
                next
            last_run = movie_dict.get(col.guid)
            if last_run is None:
                last_run = last_run = now - timedelta(days = 99999)
            else:
                last_run = last_run.get('updated')
                last_run = str_to_date(last_run)
            items = col.items()
            len(col.items())
            sync_freq = update_collection_sync_freq + round(len(col.items())/5)
            if now - timedelta(days=sync_freq) >= last_run:
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
                    i_labels.extend(plex_functions.list_movie_age_labels(i, labs_to_sync))
                i_labels = list(set(i_labels))
                c_labels = plex_functions.list_movie_age_labels(col, user_labels)
                labels_to_add = difference(i_labels, c_labels)
                labels_to_add.sort()
                labels_to_remove = difference(c_labels, i_labels)

                for label in labels_to_remove:
                    print('removing ' + label + ' from ' + col.title)
                    col.removeLabel(label).reload()

                for label in labels_to_add:
                    print('adding  ' + label + ' to ' + col.title)
                    col.addLabel(label).reload()
                movie_dict.update({col.guid: {"updated": now.strftime('%Y-%m-%d')}})
                c = c + 1
                if c % 1 == 0:
                    write_dict(movie_dict_file, movie_dict)
                    print("saved dictionary")
            else:
                print("skipping collection due to update setting")

    else:
        update_log("Skipping collection label updates")
write_dict(movie_dict_file, movie_dict)


print("-----------------------------------------------------------------------------")
print("END OF SCRIPT.")
update_log("RUN COMPLETE")
##################################################################
