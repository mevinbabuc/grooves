from bs4 import BeautifulSoup
import requests
from urllib import quote


## Settings ##
search_term = "50 cent"

# No of pages of songs to download
pages = 1

## End Settings ##

for page in range(1, pages+1):
    site = requests.get("http://grooveshark.io/search/{0}/{1}".format(quote(search_term), page))

    soup = BeautifulSoup(site.content)

    unique_song_list = list()

    for anchor in soup.findAll('a', href=True, download=True):

        if anchor['download'] in unique_song_list:
            continue
        else:
            with open(anchor['download'], 'wb') as handle:
                response = requests.get(anchor['href'], stream=True)

                if not response.ok:
                    continue

                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)
            print anchor['download'], "Downloaded"
