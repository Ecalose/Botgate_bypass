#!/usr/bin/python3
# coding:utf-8

# @Time    : 2024/4/9 15:37
# @Author  : E0tk1
# @File    : server.py
# @IDE     : PyCharm

import json
import asyncio
import websockets
from flask import Flask, request, jsonify, make_response
from threading import Thread
import time
import random
import string


def generate_random_string(length=32):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def req_handle(verChar):
    print("-----------------------------------------------------------------------------------------------")
    try:
        hmethod = request.get_json()["method"]
        hurl = request.get_json()["url"]
        htype = request.get_json()["type"]
        try:
            hheader = request.get_json()["header"]
        except:
            hheader = ""
        if htype == "json":
            hdata = request.args.get("data")
        else:
            hdata = request.get_json()["data"]
        data = "{}[][][][][][]{}[][][][][][]{}[][][][][][]{}[][][][][][]{}".format(hmethod, hurl, htype, hdata, hheader)
        print("请求信息：")
        # print("校验码：" + verChar)
        print("Method：{}".format(hmethod))
        print("URL：{}".format(hurl))
        print("Content-type：{}".format(htype))
        print("Headers：{}".format(hheader))
        print("Data：{}".format( hdata))
        data = verChar + "------" + str(data)
        return data
    except:
        print("发送给web客户端的消息：\ndata数据错误")
        print("-----------------------------------------------------------------------------------------------")
        return None


app = Flask(__name__)
try:
    app.json.ensure_ascii = False               # 解决json中文乱码问题(flask 2.3.0以上)
except:
    app.config['JSON_AS_ASCII'] = False         # 解决json中文变Unicode编码(flask 2.2.5以下)
connected_clients = set()
loop = None  # 存储事件循环引用

message = ""
last_connect = None


@app.route('/api', methods=['POST'])
def receive_data():
    verChar = str(generate_random_string())
    data = req_handle(verChar)
    if not data:
        return "data数据错误"
    if loop is not None and last_connect:
        loop.call_soon_threadsafe(send_data_to_client, last_connect, data)
    else:
        print("ws客户端未连接")
        return "ws客户端未连接"
    start_time = time.time()
    while time.time() - start_time < 2:
        try:
            messages1 = message.split("------")
            newmessages0 = messages1[0]     # 返回的校验码
            newmessages1 = messages1[1]     # 返回的状态码
            newmessages2 = messages1[2]     # 返回的响应头
            newmessages3 = messages1[3]     # 返回的响应体
            if verChar == newmessages0:
                print("响应信息：")
                print("Code：" + str(newmessages1))
                print("Headers：" + newmessages2)
                print("Data：" + newmessages3)
                print("-----------------------------------------------------------------------------------------------")

                if newmessages2 == "0" and newmessages3 == "0":
                    return "网站访问失败，请检查\n1、URL是否正确！\n2、是否存在跨域访问\n3、网站是否能正常访问"
                newheaders = json.loads(newmessages2)
                if 'content-type' in map(str.lower, newheaders.keys()) and 'application/json' in newheaders["content-type"]:
                    response_data = json.loads(newmessages3)
                    response = jsonify(response_data)
                    for key, value in newheaders.items():
                        response.headers[key] = value
                    response.status_code = int(newmessages1)
                    print(response.data)
                    return response
                else:
                    response = make_response(newmessages3, int(newmessages1))
                    for key, value in newheaders.items():
                        response.headers[key] = value
                    return response
        except:
            time.sleep(0.1)
    print("发送给web客户端的消息：\n发送给了ws客户端，但是没有返回！\n请检查：\n1、网站访问时间是否超过2秒\n2、ws客户端已端口连接")
    print("-----------------------------------------------------------------------------------------------")
    return "发送给了ws客户端，但是没有返回！\n请检查：\n1、网站访问时间是否超过2秒\n、ws客户端已端口连接"


async def handle_client(websocket, path):
    global message, last_connect
    last_connect = websocket    # 保证消息只发送给最新连接的ws客户端
    connected_clients.add(websocket)

    token = await websocket.recv()
    if token != 'password=123456':   # ws连接密码
        await websocket.close()
        return

    client_address = websocket.remote_address

    try:
        headers = websocket.request_headers
        oriin = headers.get('Origin')
    except:
        oriin = ""
    print("ws客户端连接成功，IP：{}，端口：{}，所在站点域名：{}".format(client_address[0], client_address[1], oriin))
    await websocket.send("success!")

    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            connected_clients.remove(websocket)
            break


def send_data_to_client(websocket, data):
    try:
        asyncio.run_coroutine_threadsafe(websocket.send(data), loop)
    except websockets.exceptions.ConnectionClosed:
        connected_clients.remove(websocket)


def start_ws_server():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = websockets.serve(handle_client, "0.0.0.0", 8765)
    loop.run_until_complete(server)
    loop.run_forever()


def start_flask_app():
    app.run("127.0.0.1", port=3000)


if __name__ == '__main__':
    # 启动 Flask 和 WebSocket 服务器
    flask_thread = Thread(target=start_flask_app)
    flask_thread.start()
    start_ws_server()