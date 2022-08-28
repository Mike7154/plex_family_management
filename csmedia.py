# pylama:ignore=W0401,W0612

import requests
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime
from general_functions import *


def cl_search_txt(soup, class_str, index = 0):
    container = soup.select(class_str)
    return container[index].text


def restrip(str, find, replace=""):
    out = str.replace(find, replace)
    return out.strip()


def text_add(str, add, pretext="\n"):
    return str + pretext + add


def build_url(movie_title, lib_type, dict, library_types = ['movie', 'show']):
    base_url = dict.get('base')
    if lib_type == library_types[0]:
        base_url = dict.get('movie')
    elif lib_type == library_types[1]:
        base_url = dict.get('tv')
    else:
        return ""
    print(movie_title)
    movie_title = re.sub("[^a-zA-Z0-9 ']", '', movie_title)
    movie_title = re.sub(' ', '%20', movie_title)
    URL = base_url + movie_title
    return URL


def get_age(date):
    age = datetime.now()-date
    age = age.total_seconds()
    age = age/3600
    age = age/24
    age = age/365
    return age



def page_search(urls, search, lib, movie_dict, backup_search = ""):
    for u in urls:
        url = u
        backup_url = None
        # print(u)
        page = requests.get(u)
        search_m = re.search(str(search), page.text)
        if search_m is not None:
            print(u)
            break
        else:
            if backup_search != "":
                search_t = re.search(str(backup_search), page.text)
                if search_t is not None:
                    backup_url = url
                    search_t = None
            url = None
            page = None
            time.sleep(0.4) # I put this line in to offload Common Sense requests during large server get_search_results
            #- The above line should only slow down the first server run
    if url is None and backup_url is not None:
        url = backup_url
        page = requests.get(backup_url)
    return [page,url]


def get_search_results(URL, url_match, url_dict, skip_urls=[]):
    search_page = requests.get(URL)
    soup = BeautifulSoup(search_page.content, 'html.parser')
    links = soup.find_all('a', href=re.compile('^' + url_match))
    urls = []
    for link in links:
        b = url_dict.get('base')
        link = link.get('href')
        url = b + link
        if url not in urls and url not in skip_urls:
            urls.append(url)
    return urls

#url = "https://www.commonsensemedia.org/movie-reviews/dc-league-of-super-pets"
def scrape_CSM_page(movie_dict, page, parents_review = False):
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        to_know = cl_search_txt(soup, "div[class^=review-view-parents-need-know]")
        to_know = restrip(to_know, "Show more")
        to_know = restrip(to_know, "\n\n", "\n")
        to_know = restrip(to_know, "\n\n", "\n")
        # print(to_know)
        if parents_review == True:
            age = cl_search_txt(soup, "span[class^=rating__age]",1)
        else:
            age = cl_search_txt(soup, "span[class^=rating__age]")
        age = age.strip()
        non_decimal = re.compile(r'[^\d.]+')
        cs_age = non_decimal.sub('', age)
        movie_dict.update({"cs_age": int(cs_age)})
        div = soup.select("div[class^=content-grid-item]")
        text = "[Common Sense Media]"
        text = text_add(text, age, " ")
        text = text_add(text, to_know, "\n")
        # print(text)
        for d in div:
            x = restrip(d.text, "Not present", "")
            s = d["data-text"]
            s = re.sub('<[^>]*>', '', s)
            s = re.sub('Did you know [^?.!]*[?.!]', '', s)
            s = re.sub('Adjust limits [^?.!]*[?.!]', '', s)
            s = restrip(s, "Join now")
            s = s.strip()
            text = text_add(text, x, "\n|")
            text = text_add(text, s, "|: ")
        now = datetime.now()
        text = restrip(text, "\n\n\n", "\n")
        text = restrip(text, "\n\n", "\n")
        text = restrip(text, "\n\n", "\n")
        text = text_add(text, "[Date:" + now.strftime('%Y-%m-%d') + "]")
        movie_dict.update({'cs_summary': text})
    else:
        print("ERROR BAD STATUS CODE")
        print(URL)
    return movie_dict


def CSM_get(movie, movie_dict, movies, lib_type='movie', url_dict = {}, update_age_factor = 1, library_types = ['movie', 'show'], parents_review = False):  # Download information from Common Sense media
    updated = movie_dict.get('updated')
    if updated is not None:  # Skip the movie if it's been updated recent enough. Whether or not found/verified
        updated = datetime.strptime(updated, '%Y-%m-%d')
        oaa = movie.originallyAvailableAt
        if oaa is None:
            oaa = datetime.strptime('2010-01-01', '%Y-%m-%d')
        m_age = get_age(oaa)
        s_age = get_age(updated)
        if m_age/s_age > update_age_factor and s_age < 5:
            return movie_dict
    updated = datetime.now()
    imdb = [guid.id for guid in movie.guids if 'imdb' in guid.id]
    if len(imdb) == 0:
        update_log(movie.title + " Doesn't have an IMDbId in Plex")
        imdb = 'NOMATCH'
    else:
        imdb = re.sub('imdb://', '', imdb[0])
    # Check if the URL was verified against IMDB
    if movie_dict.get('verified') is True:
        url = movie_dict.get('url')
        page = requests.get(url)
    else:
        rep = 2
        url = None
        page = None
        URL = build_url(movie.title, lib_type, url_dict, library_types)
        backup_url = None
        print("searching " + movie.title + " in common sense media")
        if lib_type == library_types[0]:
            find_u = url_dict.get('movie_reviews')
        elif lib_type == library_types[1]:
            find_u = url_dict.get('tv_reviews')
        urls = get_search_results(URL, find_u, url_dict)
        while rep > 0:  # I want to re-search using a shorter search with this
            if len(urls) > 0:
                psearch = page_search(urls, imdb, movies, movie_dict, '\"'+movie.title +'\"')
                page = psearch[0]
                url = psearch[1]
                if backup_url is None and len(urls) == 1 and rep == 2:
                    backup_url = urls[0]
            if (len(urls) == 0 or url is None) and rep != 0:
                print(movie.title + ' search had no verified results, trying a shorter search')
                m_title = re.sub("The ", "", movie.title)
                m_title = movie.title[0:7]
                URL = build_url(m_title, lib_type, url_dict, library_types)
                urls = get_search_results(URL, find_u, url_dict, urls)
                rep = rep - 1
            else:
                rep = 0
    if url is None and backup_url is not None:
        url = backup_url
        page = requests.get(url)
        print(movie.title + " Search only showed 1 unverified result. I'm going to use that")
    if page is None:  # if no page
        movie_dict.update({"updated": updated.strftime('%Y-%m-%d')})
        movie_dict.update({"verified": False})
        update_log(movie.title + ": Missing from Common Sense Media")
        return movie_dict
    # print(url)
    movie_dict.update({"url": url})
    search_m = re.search(str(imdb), page.text)
    if search_m is not None:
        movie_dict.update({"verified": True})
    else:
        movie_dict.update({"verified": False})
        update_log(movie.title + ": Unverified IMDb match")
        print(movie.title + " was pulled in but the match could not be verified")
    movie_dict = scrape_CSM_page(movie_dict, page, parents_review)
    return movie_dict


def CSM_age(summary):  # Get date that Common Sense Media was updated
    match = re.search('\[Date:[12345677890-]*\]', summary)
    d = match.group()
    date = d[6:int(len(d)-1)]
    date = datetime.strptime(date, '%Y-%m-%d')
    return get_age(date)


def check_csm(movie):
    return "[Common Sense Media]" in movie.summary


def should_i_get_csm(movie, update_old_summaries = True, update_age_factor = 1):
    b = False
    if check_csm(movie) is False:
        b = True
    else:
        if update_old_summaries is True:
            m_age = get_age(movie.originallyAvailableAt)
            s_age = CSM_age(movie.summary)
            if m_age/s_age < update_age_factor or s_age > 10:
                b = True
    return b


def remove_csm(movie):
    s = movie.summary
    if check_csm(movie):
        summary = s
        m1 = match = re.search('\[Common Sense Media\]', summary)
        m2 = re.search('\[Date:[12345677890-]*\]', summary)
        start = m1.start()
        if m2 is None:
            end = len(summary)
        else:
            end = m2.end()
        s = summary[0:start]+summary[end:len(summary)]
        s = s.strip()
    return s
