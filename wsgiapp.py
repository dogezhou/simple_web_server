#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.parse


def run_application(application):
    """Server code."""
    # This is where an application/framework stores
    # an HTTP status and HTTP response headers for the server
    # to transmit to the client
    headers_set = []
    # Environment dictionary with WSGI/CGI variables
    environ = {}

    def start_response(status, response_headers, exc_info=None):
        headers_set[:] = [status, response_headers]

    # Server invokes the ‘application' callable and gets back the
    # response body
    result = application(environ, start_response)
    # Server builds an HTTP response and transmits it to the client

def app(environ, start_response):
    """A barebones WSGI application.

    This is a starting point for your own Web framework :)
    """
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)
    print(environ)
    name = environ['PATH_INFO']
    # >>> urllib.parse.unquote('/%E5%91%A8%E4%BC%9F')
    # '/周伟'
    # 把 URL 解码
    name = urllib.parse.unquote(name)[1:]   # '周伟'
    return ['<h1>Hello {name} from a simple WSGI application!</h1>'.format(name=name)]

# run_application(app)