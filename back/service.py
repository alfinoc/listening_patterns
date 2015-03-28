import json
from threading import Condition
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest

from cache import RedisWrapper
from lastfm import LastFMProxy
from sanitize import sanitizeHistograms

def _getParams(args, required):
   missing = []
   found = []
   for key in required:
      if key in args:
         found.append(args[key])
      else:
         missing.append(key)

   if len(missing) != 0:
      raise ValueError('Missing arguments: ' + ', '.join(missing))

   return found

def _stringify(obj, pretty=False):
   if pretty:
      return json.dumps(obj, indent=3, separators=(',', ': '))
   else:
      return json.dumps(obj)

class ConditionalStorage():
   def __init__(self):
      self.cv = Condition()
      self.data = None

   def set(self, value):
      with self.cv: self.data = value

   def get(self):
      while self.data == None:
         with self.cv: self.cv.wait()
      return self.data

class Service:
   def get_artists(self, request):
      try:
         user, = _getParams(request.args, ['user'])
      except ValueError as e:
         return BadRequest(str(e))

      if self.cache != None and self.cache.contains((user)):
         return Response(self.cache.get((user)))

      artists = ConditionalStorage()
      self.lastfm.artists(user, artists.set)
      result = _stringify({'artists': artists.get()}, True)
      if self.cache != None:
         self.cache.set((user), result)
      return Response(result)

   def get_counts(self, request):
      try:
         user, artist = _getParams(request.args, ['user', 'artist'])
      except ValueError as e:
         return BadRequest(str(e))

      if 'mbid' in request.args:
         mbid = request.args['mbid'].strip()
         if mbid == '':
            mbid = None
      else:
         mbid = None
      cacheKey = (user, artist, mbid)

      # Fast path: histograms are cached locally.
      if self.cache != None and self.cache.contains(cacheKey):
         return Response(self.cache.get(cacheKey))

      # Slow path: histograms are requested from Last.fm then cached locally.
      else:
         histograms = ConditionalStorage()
         albums = ConditionalStorage()
         eps = ConditionalStorage()
         self.lastfm.albumHistograms(user, artist, histograms.set)
         if mbid != None:
            self.lastfm.albums(mbid, 'album', albums.set)
            self.lastfm.albums(mbid, 'ep', eps.set)
         else:
            albums.set([])
            eps.set([])
         knownAlbums = set(albums.get() + eps.get())
         print 'known as reported', knownAlbums
         result = _stringify({
            'histograms': sanitizeHistograms(knownAlbums, histograms.get()),
            'unclean': histograms.get()
         }, True)
         if self.cache != None:
            self.cache.set(cacheKey, result)
         return Response(result)

   """
   dispatch requests to handlers above
   """
   def __init__(self, cached=True):
      self.url_map = Map([
         Rule('/artists', endpoint='artists'),
         Rule('/counts', endpoint='counts'),
      ])

      if cached:
         self.cache = RedisWrapper()
      else:
         self.cache = None
      self.lastfm = LastFMProxy()

   def wsgi_app(self, environ, start_response):
      request = Request(environ);
      response = self.dispatch_request(request);
      return response(environ, start_response);

   def __call__(self, environ, start_response):
      return self.wsgi_app(environ, start_response)

   def dispatch_request(self, request):
      adapter = self.url_map.bind_to_environ(request.environ)
      try:
         endpoint, values = adapter.match()
         return getattr(self, 'get_' + endpoint)(request, **values)
      except HTTPException, e:
         return e
