#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迭代式的服务器，无法同时处理多个请求
"""
import socket
import urllib
from io import BytesIO
import sys

from io import StringIO


class WSGIServer(object):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        # 创建一个监听 socket
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )
        # Allow to reuse the same address
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind
        listen_socket.bind(server_address)
        # Activate
        listen_socket.listen(self.request_queue_size)
        # Get server host name and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # Return headers set by Web framework/Web application
        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        listen_socket = self.listen_socket
        while True:
            # 等待新的客户端连接
            self.client_connection, client_address = listen_socket.accept()
            # 处理一个请求，然后关闭客户端连接。然后
            # 循环等待下一个客户端连接
            self.handle_one_request()

    def handle_one_request(self):
        # 接受客户端的请求报文
        self.request_data = request_data = self.client_connection.recv(1024)    # bytes 类型

        self.request_data = self.request_data.decode()

        # Print formatted request data a la 'curl -v'
        # 打印请求
        print(''.join(
            '< {line}\n'.format(line=line)
            for line in request_data.splitlines()
        ))

        # 解析请求
        self.parse_request(self.request_data)
        # 用请求报文构建 environment 字典
        env = self.get_environ()


        # 用 env 字典 和 start_response 调用 application，得到 result构建响应体
        print('env=', env)
        result = self.application(env, self.start_response)

        # 使用 web 框架返回的 result 构建一个响应并发送会客户端
        self.finish_response(result)

    def parse_request(self, text):

        """
        接受请求报文，把其中的请求方法，请求路径等等，绑定到 WSGIServer对象上
        :param text: string
        text =  b'GET / HTTP/1.1\r\nHost: 127.0.0.1:8888\r\nConnection: keep-alive\r\n\r\n
                    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) \r\n\r\n'

        """
        request_line = text.splitlines()[0]     # 获取第一行 b'GET / HTTP/1.1'
        print('request_line=', request_line)
        # request_line = request_line.rstrip('\r\n')
        # Break down the request line into components
        (self.request_method,  # GET
         self.path,  # /hello
         self.request_version  # HTTP/1.1
         ) = request_line.split()  # 把 bytes 的 request_line 解码成字符串(unicode)

    def get_environ(self):
        """
        返回一个字典，key是约定好的变量名，供框架使用
        :return: dict
        """
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables
        # 要求的 WSGI 变量
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = StringIO(self.request_data)
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        # Required CGI variables
        # 要求的 CGI 变量
        env['REQUEST_METHOD']    = self.request_method  # GET
        env['PATH_INFO']         = self.path # /%E5%91%A8%E4%BC%9F 浏览器编码过的 url 需要 unquote解码，如果在此处 unquote
        # flask 错误，UnicodeEncodeError: 'latin-1' codec can't encode characters in position 1-3: ordinal not in range(256)
        env['SERVER_NAME']       = self.server_name  # localhost
        env['SERVER_PORT']       = str(self.server_port)  # 8888
        return env

    def start_response(self, status, response_headers, exc_info=None):
        """
        由 application 调用，构造响应头
        :param status: '200 OK'
        :param response_headers: [('Content-Type', 'text/plain')]
        :param exc_info:
        """
        # 添加必要的服务器头信息
        server_headers = [
            ('Date', 'Tue, 31 Mar 2015 12:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        # return self.finish_response

    def finish_response(self, result):
        """
        服务器使用调用’application’返回的数据，由’start_response’设置的状态和响应头，
        来构造HTTP响应。
        """
        try:
            # 拆分出响应状态和响应头
            status, response_headers = self.headers_set # ['200 OK', [('Date', 'Tue, 31 Mar 2015 12:54:48 GMT'), ('Server', 'WSGIServer 0.2')]
            # 构建响应 response 字符串
            # 响应状态
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            # 响应头
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            # 响应体
            response += '\r\n'
            for data in result:
                # flask 返回的是Bytes, 解码成字符串, wsgiapp.py 返回的是字符串，不需要decode
                # 转换成字符串
                if isinstance(data, bytes):
                    data = data.decode()
                response += data


            # Print formatted response data a la 'curl -v'
            # 打印响应数据
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()
            ))

            self.client_connection.sendall(response.encode('utf-8'))
        finally:
            # 关闭连接
            self.client_connection.close()


# 服务器 监听 IP 和 端口
SERVER_ADDRESS = (HOST, PORT) = '127.0.0.1', 8888


def make_server(server_address, application):
    """
    :param server_address: ('127.0.0.1', 8888)
    :param application: callable对象
    :return: WSGIServer对象
    """
    # 初始化 WSGIServer 对象
    server = WSGIServer(server_address)
    # 传入可执行 application
    server.set_app(application)
    return server


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable.\n'
                 '以 module:callable 的形式提供一个 WSGI application 对象')
    app_path = sys.argv[1]  # app_path: 'wsgiapp:app'
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    # 传入 服务器地址端口，应用对象，返回 WSGIServer对象
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    print('http://127.0.0.1:8888')
    # 服务器运行
    httpd.serve_forever()
