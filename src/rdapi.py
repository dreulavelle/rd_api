#!/usr/bin/env python3

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

class RD:
    def __init__(self, api_token=None):
        if api_token is None:
            # If api_token is not provided, try to fetch it from environment variables
            api_token = os.getenv('RD_APITOKEN')
        if api_token is None or api_token == '':
            raise ValueError('API Token is empty, please provide a valid token.')
        
        self.rd_apitoken = api_token
        self.base_url = 'https://api.real-debrid.com/rest/1.0'
        self.header = {'Authorization': "Bearer " + str(self.rd_apitoken)}
        self.error_codes = json.load(open(os.path.join(Path(__file__).parent.absolute(), 'error_codes.json')))
        self.system = self.System(self)
        self.user = self.User(self)
        self.unrestrict = self.Unrestrict(self)
        self.traffic = self.Traffic(self)
        self.streaming = self.Streaming(self)
        self.downloads = self.Downloads(self)
        self.torrents = self.Torrents(self)
        self.hosts = self.Hosts(self)
        self.settings = self.Settings(self)

    def get(self, path, **options):
        request = requests.get(self.base_url + path, headers=self.header, params=options)
        return self.handler(request)

    def post(self, path, **payload):
        request = requests.post(self.base_url + path, headers=self.header, data=payload)
        return self.handler(request)

    def put(self, path, filepath, **payload):
        with open(filepath, 'rb') as file:
            request = requests.put(self.base_url + path, headers=self.header, data=file, params=payload)
        return self.handler(request)

    def delete(self, path):
        request = requests.delete(self.base_url + path, headers=self.header)
        return self.handler(request)

    def handler(self, request):
        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logging.error(errh)
        except requests.exceptions.ConnectionError as errc:
            logging.error(errc)
        except requests.exceptions.Timeout as errt:
            logging.error(errt)
        except requests.exceptions.RequestException as err:
            logging.error(err)
        
        try:
            if 'error_code' in request.json():
                code = request.json()['error_code']
                error_message = self.error_codes.get(code, 'Unknown Error')
                logging.error(f'Error {code}: {error_message}')
        except Exception as e:
            logging.error(f'An error occurred while handling the response: {e}')

        return request

    def check_token(self, token):
        if token is None or token == '':
            logging.error('API Token is empty, please add a token.')
        else:
            logging.info('API Token is valid')

    class System:
        def __init__(self, rd):
            self.rd = rd

        def disable_token(self):
            return self.rd.get('/disable_access_token')

        def time(self):
            return self.rd.get('/time')

        def iso_time(self):
            return self.rd.get('/time/iso')

    class User:
        def __init__(self, rd):
            self.rd = rd

        def get(self):
            return self.rd.get('/user').json()

    class Unrestrict:
        def __init__(self, rd):
            self.rd = rd

        def check(self, link, password=None):
            return self.rd.post('/unrestrict/check', link=link, password=password).json()

        def link(self, link, password=None, remote=None):
            return self.rd.post('/unrestrict/link', link=link, password=password, remote=remote).json()

        def folder(self, link):
            return self.rd.post('/unrestrict/folder', link=link)

        def container_file(self, filepath):
            return self.rd.put('/unrestrict/containerFile', filepath=filepath)

        def container_link(self, link):
            return self.rd.post('/unrestrict/containerLink', link=link)

    class Traffic:
        def __init__(self, rd):
            self.rd = rd

        def get(self):
            return self.rd.get('/traffic').json()

        def details(self, start=None, end=None):
            return self.rd.get('/traffic/details', start=start, end=end).json()

    class Streaming:
        def __init__(self, rd):
            self.rd = rd

        def transcode(self, id):
            return self.rd.get('/streaming/transcode/' + str(id)).json()

        def media_info(self, id):
            return self.rd.get('/streaming/mediaInfos/' + str(id)).json()

    class Downloads:
        def __init__(self, rd):
            self.rd = rd

        def get(self, offset=None, page=None, limit=None):
            return self.rd.get('/downloads', offset=offset, page=page, limit=limit)

        def delete(self, id):
            return self.rd.delete('/downloads/delete/'+ str(id))

    class Torrents:
        def __init__(self, rd):
            self.rd = rd

        def get(self, offset=None, page=None, limit=None, filter=None):
            return self.rd.get('/torrents', offset=offset, page=page, limit=limit, filter=filter)

        def info(self, id):
            return self.rd.get('/torrents/info/' + str(id))

        def instant_availability(self, hash):
            return self.rd.get('/torrents/instantAvailability/' + str(hash))

        def active_count(self):
            return self.rd.get('/torrents/activeCount')

        def available_hosts(self):
            return self.rd.get('/torrents/availableHosts')

        def add_file(self, filepath, host=None):
            return self.rd.put('/torrents/addTorrent', filepath=filepath, host=host)

        def add_magnet(self, magnet, host=None):
            magnet_link = 'magnet:?xt=urn:btih:' + str(magnet)
            return self.rd.post('/torrents/addMagnet', magnet=magnet_link, host=host)

        def select_files(self, id, files):
            return self.rd.post('/torrents/selectFiles/' + str(id), files=str(files))

        def delete(self, id):
            return self.rd.delete('/torrents/delete/' + str(id))

    class Hosts:
        def __init__(self, rd):
            self.rd = rd

        def get(self):
            return self.rd.get('/hosts')

        def status(self):
            return self.rd.get('/hosts/status')

        def regex(self):
            return self.rd.get('/hosts/regex')

        def regex_folder(self):
            return self.rd.get('/hosts/regexFolder')

        def domains(self):
            return self.rd.get('/hosts/domains')

    class Settings:
        def __init__(self, rd):
            self.rd = rd

        def get(self):
            return self.rd.get('/settings')

        def update(self, setting_name, setting_value):
            return self.rd.post('/settings/update', setting_name=setting_name, setting_value=setting_value)

        def convert_points(self):
            return self.rd.post('/settings/convertPoints')

        def change_password(self):
            return self.rd.post('/settings/changePassword')

        def avatar_file(self, filepath):
            return self.rd.put('/settings/avatarFile', filepath=filepath)

        def avatar_delete(self):
            return self.rd.delete('/settings/avatarDelete')

