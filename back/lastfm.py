import json
import grequests as async
from functools import partial
from datetime import datetime

def _toParam(key, value):
   return '&{0}={1}'.format(key, value)

EPOCH = datetime(1970, 1, 1)

class LastFMProxy:
   base_url = 'http://ws.audioscrobbler.com/2.0/?format=json&limit=1000'

   def __init__(self):
      # TODO: store in DB
      self.key = 'ef2f18ff332a62f72ad46c4820bdb11b'

   """
   calls 'callback' with a list of artist names sorted by play count by 'user'.
   """
   def artists(self, user, callback):
      process = partial(self._processArtistsData, callback)
      apiRequest = async.get(self.artistsURL(user), callback=process).send()

   """
   calls 'callback' with a dict from album name to play count histogram for that
   album, where each album is by 'artist' and each play is by 'user'. histogram
   keys are timestamps for the day in which the plays occurred.
   """
   def albumHistograms(self, user, artist, callback):
      process = partial(self._processTracksData, callback)
      apiRequest = async.get(self.tracksURL(user, artist), callback=process).send()

   """
   calls 'report' with a list of album info dicts based on the Last.fm JSON 'data'.
   names are sorted by play count. additional args contain response flags.
   """
   def _processArtistsData(self, report, data, **args):
      artists = json.loads(data.content)['topartists']['artist']
      result = map(lambda a : {'name': a['name'], 'plays': a['playcount'] }, artists)
      report(result)

   """
   calls report with a map<album name, <date, play count>> based on artistTracks
   Last.fm JSON 'data'. additional args contain response flags.
   """
   def _processTracksData(self, report, data, **args):
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

   """
   returns the URL to fetch top artist data for given 'user'.
   """
   def artistsURL(self, user):
      res = self.base_url
      res += _toParam('method', 'user.gettopartists')
      res += _toParam('api_key', self.key) 
      res += _toParam('user', user)
      return res

   """
   returns the URL to fetch logs of all scrobbles by 'user' of tracks by 'artist'.
   """
   def tracksURL(self, user, artist):
      res = self.base_url
      res += _toParam('method', 'user.getartisttracks')
      res += _toParam('api_key', self.key)
      res += _toParam('user', user)
      res += _toParam('artist', artist)
      return res
