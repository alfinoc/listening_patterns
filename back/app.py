if __name__ == '__main__':
   from werkzeug.serving import run_simple
   from wsgi import create_app
   from sys import argv
   # for debugging/development, set use_debugger=True, use_reloader=True,
   run_simple('localhost', 5000, create_app(False), use_reloader=True)
