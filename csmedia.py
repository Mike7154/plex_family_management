import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from  settings import *

def cl_search_txt(soup, class_str):
    container = soup.select(class_str)
    return container[0].text

def restrip(str,find,replace = ""):
    out = str.replace(find,replace)
    return out.strip()

def text_add(str, add, pretext = "\n"):
    return str + pretext + add

def build_url(title, base=csm_base_URL):
    URL = re.sub('&','and',title)
    URL = re.sub('·','-',URL)
    URL = re.sub('[^a-zA-Z0-9 -]', '', URL)
    URL = re.sub(' ','-',URL)
    URL = re.sub('--','-',URL)
    URL = base+URL
    return URL

def get_page(URL):
    page = requests.get(URL)
    if page.status_code == 404:
        URL = re.sub('1','i',URL)
        URL = re.sub('2','ii',URL)
        URL = re.sub('3','iii',URL)
        URL = re.sub('4','iv',URL)
        URL = re.sub('5','v',URL)
        page = requests.get(URL)
        if page.status_code == 404:
            URL = re.sub('IV','4',URL)
            URL = re.sub('III','3',URL)
            URL = re.sub('II','2',URL)
            URL = re.sub('I','1',URL)
            page = requests.get(URL)
    return page

def get_age(date):
    age = datetime.now()-date
    age = age.total_seconds()
    age = age/3600
    age = age/24
    age = age/365
    return age

#URL = "https://www.commonsensemedia.org/movie-reviews/paws-of-fury-the-legend-of-hank"
#URL = "https://www.commonsensemedia.org/movie-reviews/spider-man-into-the-spider-verse"

def CSM_get(movie_title, year =""):#Download information from Common Sense media
    URL = build_url(movie_title)
    page = get_page(URL)
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
        text = text_add(text, to_know, "\n")
        #print(text)
        for d in div:
            x = restrip(d.text,"Not present","")
            s = d["data-text"]
            s=re.sub('<[^>]*>', '', s)
            s=re.sub('Did you know [^?.!]*[?.!]','',s)
            s=re.sub('Adjust limits [^?.!]*[?.!]','',s)
            s = restrip(s, "Join now")
            s = s.strip()
            text = text_add(text, x, "\n|")
            text = text_add(text,s, "|: ")
        now = datetime.now()
        text = text_add(text,"[Date:" + now.strftime('%Y-%m-%d') +"]")
        return text
    else:
        print("ERROR BAD STATUS CODE")
        print (URL)
        return ""

def CSM_age(summary):#Get date that Common Sense Media was updated
    match=re.search('\[Date:[12345677890-]*\]',summary)
    d = match.group()
    date = d[6:int(len(d)-1)]
    date = datetime.strptime(date, '%Y-%m-%d')
    return get_age(date)

def check_csm(movie):
    return "[Common Sense Media]" in movie.summary

def should_i_get_csm(movie):
    b = False
    if check_csm(movie) == False:
        b = True
    else:
        if update_old_summaries == True:
            m_age = get_age(movie.originallyAvailableAt)
            s_age = CSM_age(movie.summary)
            if m_age/s_age < update_age_factor or s_age > 5:
                b = True
    return b

def remove_csm(movie):
    s = movie.summary
    if check_csm(movie):
        summary = s
        m1 = match=re.search('\[Common Sense Media\]',summary)
        m2=re.search('\[Date:[12345677890-]*\]',summary)
        start = m1.start()
        if m2 is None:
            end = len(summary)
        else:
            end = m2.end()
        s = summary[0:start-2]+summary[end:len(summary)]
    return s

def CSM_approve_age(movie_title, year = ""):#Download information from Common Sense media
    URL = build_url(movie_title)
    page = get_page(URL)
    print(page.status_code)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        age = cl_search_txt(soup,"span[class^=rating__age]")
        age = age.strip()
        non_decimal = re.compile(r'[^\d.]+')
        age = non_decimal.sub('', age)
        return age
    else:
        print("ERROR BAD STATUS CODE")
        print (URL)
        return ""
