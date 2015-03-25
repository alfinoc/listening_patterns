from json import dumps, loads
import redis

HOST = 'localhost'
PORT = '6379'

def toDBKey(components):
   return ':'.join(components)

class RedisWrapper:
   def __init__(self):
      try:
         self.store = redis.Redis(HOST, port=PORT)
      except redis.ConnectionError:
         raise IOError

   def set(self, key, value):
      self.store.set(toDBKey(key), value)

   def get(self, key):
      return self.store.get(toDBKey(key))

   def contains(self, key):
      return self.store.exists(toDBKey(key))
