from functools import partial

MAX_BUCKETS = 70
SECS_PER_DAY = 60 * 60 * 24

def _mergeDicts(dict, accumulator):
   for key in dict:
      if not key in accumulator:
         accumulator[key] = 0
      accumulator[key] += dict[key]

def _dictSum(d1, d2):
   res = {}
   _mergeDicts(d1, res)
   _mergeDicts(d2, res)
   return res

def _isKnown(knownAlbums):
   def nonEmpty(album):
      return len(album.strip()) != 0

   def isKnown(album):
      if knownAlbums == None:
         return True
      for k in knownAlbums:
         if album in k or k in album:
            return True
      return False

   checks = [isKnown, nonEmpty]
   return lambda album : all([ fn(album) for fn in checks ])

def sanitizeHistograms(knownAlbums, histograms):
   clean, unknown = gatherUnknown(knownAlbums, histograms)
   correctSubstrings(clean)
   if len(unknown) != 0:
      clean['Other'] = unknown
   crunchBuckets(clean)
   return clean

def gatherUnknown(knownAlbums, histograms):
   # When we lack any album info, ignore known album filters.
   # TODO: This is clumsy. Could use a better state -> check set system.
   if len(knownAlbums) == 0:
      checker = _isKnown(None)
   else:
      checker = _isKnown(map(lambda a : a.lower(), knownAlbums))
   clean = {}
   unknown = {}
   for album in histograms:
      if checker(album.lower()):
         clean[album] = histograms[album]
      else:
         _mergeDicts(histograms[album], unknown)
   return clean, unknown

def correctSubstrings(histograms):
   def substr(a, b):
      return a.lower() != b.lower() and a.lower() in b.lower()
   albums = histograms.keys()
   for album in albums:
      for other in albums:
         if (other in histograms and substr(album, other)):
            _mergeDicts(histograms[other], histograms[album])
            del histograms[other]

def crunchBuckets(histograms):
   totalBuckets = set()
   for album in histograms:
      for time in histograms[album]:
         totalBuckets.add(time)

   if len(totalBuckets) <= MAX_BUCKETS:
      return  # No work to be done.

   offset = int(min(totalBuckets))
   def adjust(interval, time):
      step = (int(time) - offset) / (interval * SECS_PER_DAY)
      return offset + step * interval * SECS_PER_DAY

   def numBuckets(interval):
      return len(set(map(partial(adjust, interval), totalBuckets)))

   def incrUntilLimit(limit=1000):
      interval = 1
      while numBuckets(interval) > MAX_BUCKETS and interval < limit:
         interval += 1
      return interval
   
   interval = incrUntilLimit()
   for album in histograms:
      hist = histograms[album]
      adjHist = {}
      for time in hist:
         adjTime = adjust(interval, time)
         if adjTime not in adjHist:
            adjHist[adjTime] = 0
         adjHist[adjTime] += hist[time]
      histograms[album] = adjHist
