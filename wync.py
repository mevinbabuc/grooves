import requests
import base64
import hmac
import hashlib
import urllib
import uuid


class Wync(object):
    _host = "https://sapi.wynk.in"
    _default_headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'accept': "application/json, text/plain, */*",
        'origin': "https://music.wynk.in",
        'x-bsy-iswap': "true",
        'dnt': "1",
        'referer': "https://music.wynk.in/music/index.html",
        'accept-language': "en,en-GB;q=0.8",
        'cache-control': "no-cache"
    }

    def __init__(self, device_id=None, user_agent=None):

        if user_agent:
            self._default_headers['user-agent'] = user_agent

        self._device_id = device_id or uuid.uuid4().hex
        self._login()

    def _login(self):

        url = "{0}/music/v3/account/login".format(self._host)
        headers = {
            'x-bsy-cid': self._get_client_salt(url=url),
        }
        headers.update(self._default_headers)
        response = requests.post(
            url,
            json={
                "deviceId": self._device_id
            },
            headers=self._default_headers
        )

        resp_json = response.json()

        self._uid = resp_json['uid']
        self._token = resp_json['token']

        if response.status_code == 200:
            return self

    def _get_wync_token(self, url, method='GET'):
        message = self._prepare_message(url, method)
        secret_hash = self._get_hash(message)

        return self._uid + ":" + secret_hash.decode('utf-8')[:-1]

    def _get_hash(self, message):
        token = bytes(self._token, 'utf-8')
        message = bytes(message, 'utf-8')

        digest = hmac.new(token, message, hashlib.sha1).digest()
        return base64.encodestring(digest)

    def _prepare_message(self, url, method='GET'):
        url_pr = urllib.parse.urlparse(url)
        final_url = url_pr.path + "?" + url_pr.query
        return method + final_url

    def _get_client_salt(self, url):
        url_pr = urllib.parse.urlparse(url)
        final_url = url_pr.path + "?" + url_pr.query
        salt_key = final_url + "51ymYn1MS"
        return hashlib.sha1(salt_key.encode('utf-8')).hexdigest()

    def search(self, query, search_type='SONG'):
        """
        query: Search query
        search_type: song, album, artist, playlist
        """
        url = "{0}/music/v1/unisearch?q={1}&lang=en".format(self._host, query)

        headers = {
            'x-bsy-cid': self._get_client_salt(url=url),
        }
        headers.update(self._default_headers)
        response = requests.get(url, headers=headers)

        search_type_map = {
            'SONG': 0,
            'ALBUM': 1,
            'ARTIST': 2,
            'PLAYLIST': 3,
        }

        if response.status_code == 200:
            resp_json = response.json()
            search_data = resp_json['items'][search_type_map[search_type]]

            for index, each in enumerate(search_data['items']):
                print(str(index) + " > ", each['title'])

            song_id = int(input("Enter the song ID you want to download > "))

            try:
                self.download(
                    search_data['items'][song_id]['id'],
                    search_data['items'][song_id]['title']
                )
            except IndexError:
                print("Not a valid option")

    def download(self, song_id, name="no-name"):
        url = "{0}/music/v1/cscgw/{1}.html?sq=m".format(self._host, song_id)

        headers = {
            'x-bsy-cid': self._get_client_salt(url=url),
            'x-bsy-utkn': self._get_wync_token(url=url),
        }
        headers.update(self._default_headers)
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            resp_json = response.json()
            download_url = resp_json['url']

            song = requests.get(download_url)
            if song.status_code == 200:
                with open(name + '.mp3', 'wb') as f:
                    f.write(song.content)
                    print("\tsong {0} download!".format(name))


if __name__ == '__main__':

    try:
        import fire
    except ImportError:
        print("Install Fire: pip install fire")
    else:
        fire.Fire(Wync)
