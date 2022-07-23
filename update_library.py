import csmedia
import plex_functions
import configparser

plex = plex_connect()
print(plex)

movies = plex.library.section('Movies')
for movie in movies.all()[0:1]:
    print(movie.title)
    print(movie.summary)
    print(build_url(movie.title))
    #sum = text_add(movie.summary, "test")
    movie.editSummary(sum)


URL = "https://www.commonsensemedia.org/movie-reviews/spider-man-into-the-spider-verse"
csm = CSM_get(URL)
#match=re.search('\[Date:[12345677890-]*\]',csm)
#print(csm)
#print("Match at index %s, %s" % (match.start(), match.end()))
#print(csm[match.start():match.end()])
#match2=re.search('\[Common Sense Media\]',csm)
#print("Match at index %s, %s" % (match2.start(), match2.end()))
with open('settings.ini', 'w') as configfile:
    config.write(configfile)
