import json
import grequests as async
from functools import partial
from datetime import datetime
from unidecode import unidecode

def _paramSuffix(params):
   return unidecode('&'.join(map(lambda key : u'{0}={1}'.format(
      key, params[key]), params)))

def _mergeDicts(dict, accumulator):
   for key in dict:
      if not key in accumulator:
         accumulator[key] = 0
      accumulator[key] += dict[key]

EPOCH = datetime(1970, 1, 1)
ALBUM_TYPES = ['Album', 'EP']

class LastFMProxy:
   last_fm_base_url = 'http://ws.audioscrobbler.com/2.0/?'
   mb_base_url = 'http://musicbrainz.org/ws/2/release-group?'

   def __init__(self):
      # TODO: store in DB
      self.key = 'ef2f18ff332a62f72ad46c4820bdb11b'

   def sanitizeHistograms(self, knownAlbums, histograms):
      if len(knownAlbums) == 0:
         return histograms
      knownAlbums = set(map(lambda a : a.lower(), knownAlbums))
      def match(a):
         for k in knownAlbums:
            if a in k or k in a:
               return True
         return False
      clean = {}
      unknown = {}
      for album in histograms:
         if match(album.lower()):
            clean[album] = histograms[album]
         else:
            _mergeDicts(histograms[album], unknown)
      if len(unknown) != 0:
         clean['Other'] = unknown
      return clean

   """
   calls 'callback' with a list of artist names sorted by play count by 'user'.
   if 'recent', uses recent artists for the user; otherwise, uses top artists
   """
   def artists(self, user, callback, recent=False):
      if recent:
         handler = self._processRecentArtistsData
         url = self.recentArtistsURL
      else:
         handler = self._processTopArtistsData
         url = self.topArtistsURL
      process = partial(handler, callback)
      async.get(url(user), callback=process).send()

   """
   calls 'callback' with a dict from album name to play count histogram for that
   album, where each album is by 'artist' and each play is by 'user'. histogram
   keys are timestamps for the day in which the plays occurred.
   """
   def albumHistograms(self, user, artist, callback):
      process = partial(self._processTracksData, callback)
      print self.tracksURL(user, artist)
      async.get(self.tracksURL(user, artist), callback=process).send()

   """
   calls 'callback' with a list of the top albums for the given 'artist'.
   """
   def albums(self, mbid, type, callback):
      process = partial(self._processAlbumsData, callback)
      async.get(self.albumsURL(mbid, type), callback=process).send()

   """
   calls 'report' with a list of album info dicts based on the Last.fm JSON 'data'.
   names are sorted by play count. additional args contain response flags.
   """
   def _processTopArtistsData(self, report, data, **args):
      try:
         artists = json.loads(data.content)['topartists']['artist']
         report(map(lambda a : {
            'name': a['name'],
            'plays': a['playcount'],
            'mbid': a['mbid']
         }, artists))
      except:
         report([])

   def _processRecentArtistsData(self, report, data, **args):
      #try:
      tracks = json.loads(data.content)['recenttracks']['track']
      seen = set()
      unique = []
      for t in tracks:
         name = t['artist']['#text']
         if name not in seen:
            unique.append({
               'name': name,
               'last': t['date']['uts'],
               'mbid': t['artist']['mbid']
            })
            seen.add(name)
      report(unique)
      #except:
      #   report([])

   """
   calls report with a map<album name, <date, play count>> based on artistTracks
   Last.fm JSON 'data'. additional args contain response flags.
   """
   def _processTracksData(self, report, data, **args):
      try:
         result = {}
         artistTracks = json.loads(data.content)['artisttracks']
         utc = lambda date : int((date - datetime(1970, 1, 1)).total_seconds())
         if 'track' in artistTracks:
            tracks = artistTracks['track']
            for t in tracks:
               album = t['album']['#text']
               bucket = utc(datetime.combine(
                            datetime.fromtimestamp(float(t['date']['uts'])).date(),
                            datetime.min.time()))
               if album not in result:
                  result[album] = {}
               if bucket not in result[album]:
                  result[album][bucket] = 1
               else:
                  result[album][bucket] += 1
         report(result)
      except:
         report({})

   """
   calls report with a list of release-groups in MB JSON 'data'.
   """
   def _processAlbumsData(self, report, data, **args):
      try:
         albums = json.loads(data.content)['release-groups']
         albums = filter(lambda a : a['primary-type'] in ALBUM_TYPES, albums)
         albums = filter(lambda a : len(a['secondary-types']) == 0, albums)
         report(map(lambda a : a['title'], albums))
      except:
         report([])

   """
   returns the URL to fetch top artist data for given 'user'.
   """
   def topArtistsURL(self, user):
      return self.last_fm_base_url + _paramSuffix({
         'api_key': self.key,
         'method': 'user.gettopartists',
         'user': user,
         'format': 'json',
         'limit': 1000
      });

   def recentArtistsURL(self, user):
      return self.last_fm_base_url + _paramSuffix({
         'api_key': self.key,
         'method': 'user.getrecenttracks',
         'user': user,
         'format': 'json',
         'limit': 200
      });

   """
   returns the URL to fetch logs of all scrobbles by 'user' of tracks by 'artist'.
   """
   def tracksURL(self, user, artist):
      return self.last_fm_base_url + _paramSuffix({
         'api_key': self.key,
         'method': 'user.getartisttracks',
         'user': user,
         'artist': artist,
         'format': 'json',
         'limit': 1000
      });

   """
   returns the URL to fetch lists of albums of a given 'type' (Album or EP) for the
   artists with the given MB id.
   """
   def albumsURL(self, mbid, type):
      return self.mb_base_url + _paramSuffix({
         'artist': mbid,
         'type': type,
         'fmt': 'json'
      });
