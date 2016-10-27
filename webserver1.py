#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端建立连接，响应
"""
import socket

HOST, PORT = '127.0.0.1', 8888

# 创建一个 socket：AF_INET 指定使用 IPv4 协议，SOCK_STREAM 指定使用面向流的 TCP 协议
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 设置 socket 选项
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 监听端口：向套接字赋值一个本机某一快网卡的 IP 地址，和端口
listen_socket.bind((HOST, PORT))
# 开始监听：传入的参数指定等待连接的最大数量
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT)
print('http://127.0.0.1:8888')
while True:
    # listen 等待客户端建立一条到本地端口的连接，返回客户端的新的 socket和 地址
    client_connection, client_address = listen_socket.accept()
    # 尝试接受 1024个字节
    request = client_connection.recv(1024)
    print(request)

    http_response = b"""
HTTP/1.1 200 OK

Hello, World!
"""
    client_connection.sendall(http_response)
    client_connection.close()
