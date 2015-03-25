import json
from threading import Condition
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest

from cache import RedisWrapper
from lastfm import LastFMProxy

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

      artists = ConditionalStorage()
      self.lastfm.artists(user, artists.set)
      return Response(_stringify({'artists': artists.get()}, True))

   def get_counts(self, request):
      try:
         user, artist = _getParams(request.args, ['user', 'artist'])
      except ValueError as e:
         return BadRequest(str(e))

      # Fast path: histograms are cached locally.
      if self.cache.contains((user, artist)):
         return Response(self.cache.get((user, artist)))

      # Slow path: histograms are requested from Last.fm then cached locally.
      else:
         histograms = ConditionalStorage()
         self.lastfm.albumHistograms(user, artist, histograms.set)
         result = _stringify({'histograms': histograms.get()}, True)
         self.cache.set((user, artist), result)
         return Response(result)

   """
   dispatch requests to handlers above
   """
   def __init__(self):
      self.url_map = Map([
         Rule('/artists', endpoint='artists'),
         Rule('/counts', endpoint='counts'),
      ])
      self.cache = RedisWrapper()
      self.lastfm = LastFMProxy('DUMMY')

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
