#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一个 flask app 用来测试 webserver2.py 是否符合 WSGI
> python webserver2.py flaskapp:app
"""
import urllib.parse

from flask import Flask
from flask import Response
flask_app = Flask('flaskapp')


@flask_app.route('/<name>')
def hello_world(name):
    # >>> urllib.parse.unquote('/%E5%91%A8%E4%BC%9F')
    # '/周伟'
    # 把 URL 解码
    name = urllib.parse.unquote(name)
    return Response(
        '<h1>Hello {name} from Flask!</h1>'.format(name=name),
        mimetype='text/html'
    )

app = flask_app.wsgi_app