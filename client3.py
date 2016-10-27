#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用来测试并发服务器(不符合 WSGI)，webserver3c.py - client3.py
用来测试迭代服务器(符合 WSGI)，webserver2.py
用来测试并发服务器(符合 WSGI），webserver4.py
> python client3.py --max-conns=10
> python client3.py
"""

import argparse
import errno
import os
import socket
import threading

SERVER_ADDRESS = '127.0.0.1', 8888
REQUEST = b"""GET /hello HTTP/1.1\r\nHost: 127.0.0.1:8888\r\n\r\n"""
def make_request(max_conns):
    """
    每一个线程代表一个客户端，每一个客户端建立 max_conns 个连接
    """
    for connection_num in range(max_conns):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(SERVER_ADDRESS)
        sock.sendall(REQUEST)


def main(max_clients, max_conns):
    # 多少客户端，max_clients, 创建多少线程处理连接
    for client_num in range(max_clients):
        t = threading.Thread(target=make_request, args=(max_conns,))
        t.start()

if __name__ == '__main__':

    # 获得一个 parser 对象
    parser = argparse.ArgumentParser(
        description='Test client for LSBAWS.\n'
                    '测试服务器',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # 通过调用其add_argument()方法来设置程序可接受的命令行参数。
    # -- 开头的参数为可选参数
    parser.add_argument(
        '--max-conns',
        type=int,
        default=1024,
        help='Maximum number of connections per client.\n '
             '每一个客户端最多可以的连接数量'
    )
    parser.add_argument(
        '--max-clients',
        type=int,
        default=1,
        help='Maximum number of clients.\n '
             '客户端的最大数量'
    )

    # 调用其parse_args方法来获取一个收集了所有参数的args对象。
    args = parser.parse_args()

    # 使用获得的命令行参数调用函数
    main(args.max_clients, args.max_conns)