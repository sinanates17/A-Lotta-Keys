def application(environ, start_response):
    with open('/tmp/wsgi_env.log', 'w') as f:
        for key, value in environ.items():
            f.write(f"{key}: {value}\n")
    
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b"WSGI environment dumped.\n"]
application()

from app import app as application