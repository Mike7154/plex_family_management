# pylama:ignore=E202,E231,E265

#[LOGIN]
#-------------------------------------------------------------------------
plex_email = "YOUR_EMAIL"
plex_password = "YOUR_PASSWORD"
plex_server = "YOUR_SERVER"
#I know it's not ideal to store the password here. I'll change it later

libraries = ["Movies", "TV Shows"]
#-name of media libraries that you want to run this script for
#-------------------------------------------------------------------------

#USERS
#This is where you add all of the users that you want to control media access
#BE CAREFUL WITH SYNTAX HERE
#-------------------------------------------------------------------------
users = {"users":[
    {"username":"kid1","gender":"M", "dob":"2015-01-19", "playlist":"kid1_add"},
    {"username":"kid2","gender":"M", "dob":"2011-09-27", "playlist":""},
    {"username":"kid3","gender":"M", "dob":"2011-12-25", "playlist":"kid3_add"},
    {"username":"shared_kids","gender":"both", "dob":"2019-01-01", "playlist":"shared_account"}
]}
#-------------------------------------------------------------------------

#[RUN]
#------------------------------------------------------------------------
run_common_sense_media = True
# -This tells whether or not you want to add common sense media data to movie summaries
approve_common_sense_media_ages = True
# -This will add a label for the age recommended by common sense media when label is missing
#WARNING, THIS MAY AUTO APPROVE UNAPPROVED ITEMS UNLESS YOU USE THE unapprove_label BELOW OR ADD YOUR OWN AGE LABEL (ie. 18+ etc)
run_playlist_approve = True
# -This tells whether to approve movies that are added to a users playlist.
run_col_labels = True
# -This adds movie labels to collections. So users who can see a movie can also see that collection
run_auto_approve = True
# -This will automaically approve labels based on each users age. Every kid will get approved their age
# -'kids' label will be added to everyone for universal approval


#[UNDO]
CLEAN_LIBRARY = False
#THIS WILL REMOVE ALL COMMON SENSE MEDIA INFORMATION AND TAGS AND UNLOCK THE SUMMARY FIELDS

#-------------------------------------------------------------------------

#[PLEX]
#-------------------------------------------------------------------------

unapprove_playlist = "Unapprove_All"
#-Movies added to this playlist will become unapproved from everyone
approve_playlist = "Approve_All"
#-Movies added to this playlist will be approved for 1+

unapprove_label = "Unapproved"
#- This is the unapprove label. If blank, common sense media might add it back.
#--Make it something if you want to keep these from getting approved. You can add movies to the unapproved playlist

use_unlabeled_label = True
#- I like to add an "unlabeled" label so I can see all the movies that don't have a age label

age_label_prefix = "CS_"
age_label_suffix = "+"
#- This will append text to the beginning and end of an age label. Default label will be age (ie. 4+, 5+_girl, 10+). You can se this to "+" to make it 4+, 5+girl, 10+ if you want
days_early = 0
#- How many days before birthday should new age be approved?
gender_specific = True
gender_specific_txt = ["_girl","_boy"]
#-if true, it will approve age plus age_gender for each user. This just gives more control. (ie. only girls get the princess movies and boys get batman, if you so choose)
#-but you would have to modify these labels manually to be "5_girl" etc
#You can set an account to M F or both (for shared accounts that you want both content on)

offset_playlist_approve = 0
#-Just something I use personally. I like to give each kid their own movies, and they get excited about it.
#-With this I can add a movie to a kids playlist, and it adds it to his account and his age + offset
#Set -1 if you want to add name tag with no age tag added

update_collection_sync_freq = 7
#- Updating the collection labels takes a while, so I choose not to update it every day
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
#[CSM]
update_old_summaries = True
#- Should I update old common sense media summaries?
update_age_factor = 2
#- It will update if the movie age / summary age is less than this factor. 1 means never update.
#- 3 means update when the summary becomes one third as old as the movies
#- for a 2. The movie will update after 2mo, then 4mo, 8mo, 16mo and so on. until it spaces to 5 years
#-------------------------------------------------------------------------


#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#Variables - don't change these
csm_URLs = {
    'base': 'https://www.commonsensemedia.org',
    'movie': "https://www.commonsensemedia.org/search/category/movie/",
    'tv': 'https://www.commonsensemedia.org/search/category/tv/',
    'movie_reviews':'/movie-reviews/',
    'tv_reviews': '/tv-reviews/' }
library_types = ['movie','show']
movie_dict_file = "movie_data.json"
