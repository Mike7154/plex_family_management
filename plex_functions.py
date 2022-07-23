from plexapi.myplex import MyPlexAccount
import datetime
import configparser

#Connect to Plex
def plex_connect(server = "Mike's Media",email="mike-7154@hotmail.com",pwd="mkalcl159851"):
    PLEXAPI_PLEXAPI_TIMEOUT=200
    account = MyPlexAccount('mike-7154@hotmail.com','mkalcl159851')
    plex = account.resource("Mike's Media").connect()
    PLEXAPI_PLEXAPI_TIMEOUT=200
    return plex

def get_setting(section, setting):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        config.add_section('RUN')
        config.set('LOGIN', 'email', 'mike-7154@hotmail.com')
        config.set('section_b', 'not_found_val', '404')


config = configparser.ConfigParser()
config.read('settings.ini')
config.add_section('USERS')
config.set('LOGIN','server',"Mike's Media")
with open('settings.ini', 'w') as configfile:
    config.write(configfile)
config.get("LOGIN","server")
