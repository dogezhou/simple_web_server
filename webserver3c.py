#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###########################################################################
# 并发服务器（用 threading) - webserver3c.py                                      #
#                                                                         #
# 在 windows 使用 threading 模块                                           #
#                                                                         #
# - 子线程处理一个请求后，睡眠60秒                                           #
# - 子线程需要先关闭客户端连接，主动关闭客户端 socket                         #
#   关闭客户端连接，如果不关闭描述符，客户端不会终止，因为客户端连接不会关闭。   #
#   服务器子进程退出，但是客户端socket没有被内核关闭掉，因为引用计数不是0啊，   #
#   所以，结果就是，终止数据包（在TCP/IP说法中叫做FIN）没有发送给客户端，       #
#   所以客户端就保持在线啦。                                                #
#
###########################################################################
import os
import socket
import threading
import time

SERVER_ADDRESS = (HOST, PORT) = '127.0.0.1', 8888
REQUEST_QUEUE_SIZE = 5

def handle_request(client_connection):
    request = client_connection.recv(1024)
    print(request.decode())
    http_response = b"""
HTTP/1.1 200 OK

Hello, World!
"""
    client_connection.sendall(http_response)
    # 关闭客户端连接，如果不关闭描述符，客户端不会终止，因为客户端连接不会关闭。
    # 服务器子进程退出，但是客户端socket没有被内核关闭掉，因为引用计数不是0啊，
    # 所以，结果就是，终止数据包（在TCP/IP说法中叫做FIN）没有发送给客户端，
    # 所以客户端就保持在线啦。
    client_connection.close()
    time.sleep(60) # 用浏览器会等 60 秒才好，命令行工具 curl 直接返回数据吗？错误，应当
    print('子线程：{name}结束'.format(name=threading.current_thread().name))

def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))

    while True:
        client_connection, client_address = listen_socket.accept()
        t = threading.Thread(target=handle_request, args=(client_connection,))
        t.start()

if __name__ == '__main__':
    serve_forever()