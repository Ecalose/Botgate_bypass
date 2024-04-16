from mitmproxy import http
import asyncio
import aiohttp
import time
from werkzeug.formparser import parse_form_data
from werkzeug.datastructures import MultiDict
from io import BytesIO


flag_req = None

jstext = '''if (typeof window.globalSocket121 !== 'undefined') {
    if (window.globalSocket121.readyState === WebSocket.CLOSED) {
        socket_start()
    }
} else {
    socket_start()
}
function socket_start(){
    const socket121 = new WebSocket('ws://127.0.0.1:8765');
    window.globalSocket121 = socket121;

    socket121.onopen = function(event) {
        socket121.send('password=123456');
    };

    socket121.onmessage = function(event) {
        const receivedMessage = event.data;

        const parts = receivedMessage.split("------------");

        const varChars = parts[0]

        const reqdata = parts[1]

        if (parts.length == 2) {
            try {
                const [newdata1, newdata2, newdata3, newdata4, newdata5] = reqdata.split("[][][][][][]");

                const fetchOptions = {};
                const headers = {};
                if (newdata5 !== undefined && newdata5 !== null && newdata5 !== '') {
                    const headersArray = newdata5.split('|||').map(header => header.trim().split(': '));
                    headersArray.forEach(([key, value]) => {
                        headers[key] = value;
                    });
                }

                if (newdata1 === 'POST') {
                    let str_str = newdata4;
                    fetchOptions["method"] = 'POST';
                    if (newdata3 === 'json') {
                        try {
                            str_str = JSON.parse(str_str);
                        } catch (error) {
                            throw new Error('Failed to parse JSON data');
                        }
                        fetchOptions["body"] = JSON.stringify(str_str);
                        headers["Content-Type"] = 'application/json';
                    } else if (newdata3 === 'xform') {
                        const params = new URLSearchParams();
                        if (str_str !== undefined && str_str !== null && str_str !== '') {
                            const keyValuePairs = str_str.split('&');
                            keyValuePairs.forEach(keyValue => {
                                const [key, value] = keyValue.split('=');
                                params.append(key, value);
                            });
                        }
                        fetchOptions["body"] = params;
                        headers["Content-Type"] = 'application/x-www-form-urlencoded'
                    } else if (newdata3 === 'formdata') {
                        const formData = new FormData();
                        if (newdata4 !== undefined && newdata4 !== null && newdata4 !== '') {
                            const keyValuePairs = newdata4.split('&');
                            keyValuePairs.forEach(keyValue => {
                                const [key, value] = keyValue.split('=');
                                formData.append(key, value);
                            });
                        }
                        fetchOptions["body"] = formData;
                        headers["Content-Type"] = 'multipart/form-data; boundary=----WebKitFormBoundary4PvJtCrxXwKMSAs1';
                    }
                }
                if (Object.keys(headers).length > 0) {
                    fetchOptions.headers = new Headers(headers);
                }

                fetch(newdata2, fetchOptions)
                .then(response => {
                    const statusCode = response.status.toString(); 

                    const headersJson = {};
                    response.headers.forEach((value, name) => {
                        headersJson[name] = value;
                    });
                    headersString = JSON.stringify(headersJson);

                    xydata = response.text();

                    return xydata.then(xydata => {
                        return {
                            statusCode: statusCode,
                            headersString: headersString,
                            xydata: xydata
                        };
                    });
                })
                .then(({ statusCode, headersString, xydata }) => {
                    socket121.send(varChars + '------------' + statusCode + '------------' + headersString + '------------' + xydata);
                })
                .catch(error => {
                    socket121.send(varChars + '------------0------------0------------0');
                });
            } catch (error) {
                socket121.send(varChars + '------------0------------0------------0');
            }
        }
    };
}'''

def parse_multipart_data(data, content_type):
    environ = {
        'REQUEST_METHOD': 'POST',
        'CONTENT_TYPE': content_type,
        'wsgi.input': BytesIO(data.encode()),
        'CONTENT_LENGTH': str(len(data.encode()))
    }
    stream, form, files = parse_form_data(environ)
    params = '&'.join([f"{key}={value}" for key, value in form.items()])
    return params


class CustomResponse:
    def __init__(self):
        self.num = 0

    async def request(self, flow: http.HTTPFlow) -> None:
        global flag_req
        flag_req = flow.request.headers.get("Req-flag", "")
        if flag_req:
            await self.handle_delayed_request(flow)

    async def handle_delayed_request(self, flow: http.HTTPFlow) -> None:
        url = flow.request.url
        method = flow.request.method
        headers = flow.request.headers
        newheaders = "|||".join([f"{key}: {value}" for key, value in headers.items() if key != "Req-flag"])
        content_type = flow.request.headers.get("Content-Type", "")

        if "application/json" in content_type:
            data2 = flow.request.text
            data1 = ""
            reqtype = "json"
        elif "application/x-www-form-urlencoded" in content_type:
            data1 = flow.request.text
            data2 = ""
            reqtype = "xform"
        elif "multipart/form-data" in content_type:
            if "form-data" not in str(flow.request.text):
                data1 = ""
            else:
                content_type = 'multipart/form-data; boundary=' + flow.request.text.splitlines()[0].replace("------", "----")
                # 解析数据
                data1 = parse_multipart_data(flow.request.text, content_type)
            data2 = ""
            reqtype = "formdata"
        else:
            reqtype = ""
            data1 = ""
            data2 = ""

        burp0_json = {
            "data": data1,
            "header": newheaders,
            "method": str(method),
            "type": reqtype,
            "url": url
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("http://127.0.0.1:3000/api?data=" + data2.replace("#", "%23"),
                                        headers={"Content-Type": "application/json;charset=UTF-8"},
                                        json=burp0_json) as response:
                    aa = http.Headers()
                    for key, value in response.headers.items():
                        aa.add(key, value)
                    response2 = http.Response(
                        http_version=b"HTTP/1.1",
                        status_code=response.status,
                        reason=response.reason.encode(),
                        headers=aa,
                        content=await response.read(),
                        trailers=None,
                        timestamp_start=time.time(),
                        timestamp_end=time.time()
                    )
                    flow.response = response2
        except:
            flow.response.content = "flask服务器请求失败，检查server.py是否启动"

    def response(self, flow: http.HTTPFlow) -> None:
        global jstext, flag_req
        if not flag_req:
            content_type = flow.response.headers.get("Content-Type", "").lower()
            if flow.response.text:
                if content_type.startswith("application/javascript"):
                    flow.response.text += jstext

                if content_type.startswith("text/html"):
                    flow.response.text += "<script>" + jstext + "</script>"

            if "Content-Security-Policy" in flow.response.headers:
                del flow.response.headers["Content-Security-Policy"]


addons = [
    CustomResponse()
]

