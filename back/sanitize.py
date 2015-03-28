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
   print 'in isKnown', knownAlbums
   def nonEmpty(album):
      return len(album.strip()) != 0

   def isKnown(album):
      for k in knownAlbums:
         if album in k or k in album:
            return True
      return False

   checks = [isKnown, nonEmpty]
   return lambda album : all([ fn(album) for fn in checks ])

def sanitizeHistograms(knownAlbums, histograms):
   correctSubstrings(histograms)
   res = gatherUnknown(knownAlbums, histograms)
   return res

def gatherUnknown(knownAlbums, histograms):
   if len(knownAlbums) == 0:
      return histograms
   clean = {}
   unknown = {}
   checker = _isKnown(map(lambda a : a.lower(), knownAlbums))
   for album in histograms:
      if checker(album.lower()):
         clean[album] = histograms[album]
      else:
         _mergeDicts(histograms[album], unknown)
   if len(unknown) != 0:
      clean['Other'] = unknown
   return clean

def correctSubstrings(histograms):
   def substr(a, b):
      return a.lower() != b.lower() and a.lower() in b.lower()
   albums = histograms.keys()
   for album in albums:
      for other in albums:
         if (album in histograms and substr(album, other)):
            _mergeDicts(histograms[album], histograms[other])
            del histograms[album]

def crunchBuckets():
   pass
