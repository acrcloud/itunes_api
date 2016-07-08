#!/usr/bin/env python
# coding:utf-8

import requests
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class ItunesApi:
    def __init__(self):
        self.api_url = 'https://itunes.apple.com/'

    def request(self, method, path, params=None):
        url = self.api_url + path
        r = requests.request(method, url, params=params)
        print r.url
        return r

    # media: The media type you want to search for. For example: movie. The default is all.
    # entity: The type of results you want returned, relative to the specified media type. For example: movieArtist for
    #         a movie media type search. The default is the track entity associated with the specified media type.
    # limit: The number of search results you want the iTunes Store to return. For example: 25.The default is 50.
    # lang: The language, English or Japanese, you want to use when returning search results. Specify the language using
    #       the five-letter codename. For example: en_us.The default is en_us (English).
    def search_by_keyword(self, word, media='music', country='US', entity='song', limit=10, lang='en_us'):
        results = []
        word = self.search_keywords_filter_brackets(word)
        params = {
            'term': word,
            'country': country,
            'media': media,
            'entity': entity,
            'limit': limit,
            'lang': lang,
        }
        tracks_data = self.request('GET', 'search', params).json()['results']
        for track_data in tracks_data:
            track_metadata = self.parse_track(track_data)
            results.append(track_metadata)
        return results

    # Look up an album by its UPC, including the tracks on that album:
    def search_by_upc(self, upc, title=''):
        params = {
            'upc': upc,
            'entity': 'song'
        }
        metadata = self.request('GET', 'lookup', params).json()['results']
        title = self.search_keywords_filter_brackets(title)
        return self.parse_album(metadata, title)

    # remove brackets
    @staticmethod
    def search_keywords_filter_brackets(keywords):
        keywords = keywords.replace(' ', '')
        re_str = re.compile(r'[\{\(\[].*?[\}\)\]]')
        title = re_str.sub('', keywords.strip())
        e = title.find('［')
        if e > 0:
            title = title[:e]
        e = title.find('（')
        if e > 0:
            title = title[:e]
        e = title.find('【')
        if e > 0:
            title = title[:e]
        title = title.lower()
        return title

    @staticmethod
    def parse_track(track_data):
        track_metadata = {
            'release_date': track_data.get('releaseDate'),
            'artist_id': track_data.get('artistId'),
            'artist_name': track_data.get('artistName'),
            'audio_url': track_data.get('previewUrl'),
            'album': track_data.get('collectionName'),
            'album_id': track_data.get('collectionId'),
            'title': track_data.get('trackName'),
            'track_id': track_data.get('trackId'),
            'duration': track_data.get('trackTimeMillis'),
            'genre': track_data.get('primaryGenreName'),
            'track_position': track_data.get('trackNumber')
        }
        return track_metadata

    def parse_album(self, metadata, title):
        results = []
        album_data = metadata[0]
        album_metadata = {
            'amgArtistId': album_data.get('amgArtistId'),
            'label': album_data.get('copyright'),
        }
        tracks_metadata = metadata[1:]
        for track_data in tracks_metadata:
            track_metadata = self.parse_track(track_data)
            if title:
                if title == self.search_keywords_filter_brackets(track_metadata['title']):
                    track_metadata.update(album_metadata)
                    results.append(track_metadata)
            else:
                track_metadata.update(album_metadata)
                results.append(track_metadata)
        return results

