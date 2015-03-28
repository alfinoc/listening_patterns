import os
from service import Service
from werkzeug.wsgi import SharedDataMiddleware

def create_app():
   app = Service(True)
   app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/static':  os.path.join(os.path.dirname(__file__), '../front'),
      '/charts': os.path.join(os.path.dirname(__file__), '../front/vulcanized.html'),
   })
   return app