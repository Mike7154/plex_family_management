# Plex Family Management V 1.0.6
Hello. I wrote this script to manage my kids media through plex more easily and it's working well for me.  The goal was to have more control over what media kids are exposed to through plex. This means having a plex server with managed users. This works for movies and TV shows, but TV shows is less complete.


PLEX FAMILY MANAGEMENT
I made this script to automate the management of plex users. This script includes 4 parts. You can tweak these in settings.yml

1. Common Sense Media Information
    a. This script can get parental information and add it to the movie summaries in plex if it can find the movie in common sense media

    b. This script can get common sense media age recommendation and add it to the movies as labels to automatically approve age-appropriate content
       -Note: Not all movies can be found in common sense media. It will try to verify by matching IMDB for movies (doesn't work yet for TV shows).
       -I am in the process of getting approval for an commonsense API key, but I'm not sure how that will change the process or if I will need to turn it into a webapp or if it will work for non-paid accounts. Not sure if/when I'll change it.

2. Auto Manage User Restrictions
    a. This script can automatically update a users shared restrictions to match their age. You must store the users birthdays in settings.yml

3. Approve/Unapprove movies through playlists

    a. This script allows you to approve a movie for a user by adding the movie to a specific playlist. (Allows you to approve on mobile)

4. Auto label collections

    a. This script can automatically keep collection labels in sync with it's movie labels. This way users won't see empty collections and collections aren't hidden

SETTINGS
You need to update the settings file in settings.yml.
On first run, it will copy from blank_settings and ask for the necessary settings if you leave it blank.


Prerequisites
```
cd path/to/plex_family_management
py -m pip install -r requirements.txt
```

How to run the script.
In the command line run
```
py update_library.py
```





Author Name
Michael Larsen
m6611022+code@gmail.com
