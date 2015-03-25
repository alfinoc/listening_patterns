import json
import grequests as async
from functools import partial
from datetime import datetime

def _toParam(key, value):
   return '&{0}={1}'.format(key, value)

EPOCH = datetime(1970, 1, 1)

class LastFMProxy:
   base_url = 'http://ws.audioscrobbler.com/2.0/?format=json&limit=1000'

   def __init__(self, api_key):
      self.key = api_key
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
   calls 'report' with a list of album names found in the Last.fm JSON 'data'
   response. names are sorted by play count. additional args contain response flags.
   """
   def _processArtistsData(self, report, data, **args):
      artists = json.loads(data.content)['topartists']['artist']
      result = map(lambda a : a['name'], artists)
      report(result)

   def _processTracksData(self, report, data, **args):
      # returns the timestamp for the beginning of the day containing the given
      # timestamp 'uts'.
      def timestamp(uts):
         d = datetime.fromtimestamp(float(uts))
         dt = datetime.combine(d, datetime.min.time())
         res = (dt - EPOCH).total_seconds()
         print uts, res - float(uts)
         return res

      tracks = json.loads(data.content)['artisttracks']['track']
      result = {}
      for t in tracks:
         album = t['album']['#text']
         bucket = datetime.fromtimestamp(float(t['date']['uts'])).date().isoformat()
         if album not in result:
            result[album] = {}
         if bucket not in result[album]:
            result[album][bucket] = 1
         else:
            result[album][bucket] += 1
      report(result)

   def artistsURL(self, user):
      res = self.base_url
      res += _toParam('method', 'user.gettopartists')
      res += _toParam('api_key', self.key) 
      res += _toParam('user', user)
      res = 'http://localhost:8000/topartists_dummy.json'
      return res

   def tracksURL(self, user, artist):
      res = self.base_url
      res += _toParam('method', 'user.getartisttracks')
      res += _toParam('api_key', self.key)
      res += _toParam('user', user)
      res += _toParam('artist', artist)
      res = 'http://localhost:8000/artisttracks_dummy.json'
      return res