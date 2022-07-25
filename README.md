# plex_family Management
Hello. I am not a programmer, so if someone can help me out to make this easier to use/install, I would appreciate it. I wrote this script to manage my kids media through plex more easily and it's working well for me.  The goal was to have more control over what media kids are exposed to through plex. This means having a plex server with managed users. Currently this only works for movies and not TV, but I don't think TV would be difficult in the future


PLEX FAMILY MANAGEMENT
I made this script to automate the management of plex users. This script includes 4 parts. You can tweak these in settings.py

1. Common Sense Media Information
    a. This script can get parental information and add it to the movie summaries in plex if it can find the movie in common sense media
    b. This script can get common sense media age recommendation and add it to the movies as labels to automatically approve age_appropriate content
       -Note:Not all movies can be found on common sense media due to slight name differences and missing movies. If someone finds a better way to find CSM movies
       -let me know, I imagine a programmer could find a better way. But it found 90+% of the movies on my server.
2. Auto Manage User Restrictions
    a. This script can automatically update a users shared restrictions to match their age. You must store the users birthdays in settings.py
3. Approve/Unapprove movies through playlists
    a. This script allows you to approve a movie for a user by adding the movie to a specific playlist. (Allows you to approve on mobile)
4. Auto label collections
    a. This script can automatically keep collection labels in sync with it's movie labels. This way users won't see empty collections and collections aren't hidden

Prerequisites
Plex pass is required to have managed users
requirements.txt for python libraries
I wrote this on Python 3.9. I'm not sure if older versions will work or not.

How to run the script
Update the settings.py file. To your needs
Run the update_library.py file in python
I just have a task scheduled to run the update_library.py file once per day on my server.




Author Name
Michael Larsen
m6611022+code@gmail.com
