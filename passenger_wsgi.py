import sys


def application(environ, start_responce):
    start_responce('200 OK', [('Content_type', 'text/plain')])
    return ["Hello, World! Deployed with SFTP"]
