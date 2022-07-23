import requests
import re
from bs4 import BeautifulSoup
import datetime

def cl_search_txt(soup, class_str):
    container = soup.select(class_str)
    return container[0].text

def restrip(str,find,replace = ""):
    out = str.replace(find,replace)
    return out.strip()

def text_add(str, add, pretext = "\n"):
    return str + pretext + add

def build_url(title, base="https://www.commonsensemedia.org/movie-reviews/"):
    URL = re.sub('[^a-zA-Z0-9 .-]', ' ', title)
    URL = re.sub(' ','-',URL)
    return URL
#URL = "https://www.commonsensemedia.org/movie-reviews/paws-of-fury-the-legend-of-hank"
#URL = "https://www.commonsensemedia.org/movie-reviews/spider-man-into-the-spider-verse"

def CSM_get(URL):
    page = requests.get(URL)
    print(page.status_code)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        to_know = cl_search_txt(soup,"div[class^=review-view-parents-need-know]")
        to_know = restrip(to_know,"Show more")
        to_know = restrip(to_know, "\n\n","\n")
        to_know = restrip(to_know, "\n\n","\n")
        #print(to_know)
        age = cl_search_txt(soup,"span[class^=rating__age]")
        age = age.strip()
        div = soup.select("div[class^=content-grid-item]")
        text = "[Common Sense Media]"
        text = text_add(text, age, " ")
        text = text_add(text, to_know, "\n\n")
        #print(text)
        for d in div:
            x = restrip(d.text,"Not present","")
            s = d["data-text"]
            s=re.sub('<[^>]*>', '', s)
            s=re.sub('Did you know [^?.!]*[?.!]','',s)
            s=re.sub('Adjust limits [^?.!]*[?.!]','',s)
            s = restrip(s, "Join now","")
            s = s.strip()
            text = text_add(text, x, "\n\n")
            text = text_add(text,s)
        now = datetime.datetime.now()
        text = text_add(text,"[Date:" + now.strftime('%Y-%m-%d') +"]")
        return text
    else:
        return ""
        print("ERROR BAD STATUS CODE")
