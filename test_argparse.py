#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("echo", help="echo 字符串")  # 添加名为echo的位置参数参数
args = parser.parse_args()

print(args.echo)  # 参数解析之后可以调用args对象的同名属性来获取参数

# test_argparse