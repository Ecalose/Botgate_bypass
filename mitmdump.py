from mitmproxy import http
import aiohttp
import time
import base64

flag_req = None
jstext = '''if (typeof window.globalSocket121 !== 'undefined') {if (window.globalSocket121.readyState === WebSocket.CLOSED) {socket_start();}} else {socket_start();}
function socket_start(){
    const socket121 = new WebSocket('ws://127.0.0.1:8765');
    window.globalSocket121 = socket121;
    socket121.onopen = function(event) {socket121.send('password=123456');};
    socket121.onmessage = function(event) {
        const receivedMessage = atob(event.data);const parts = receivedMessage.split("------------");const varChars = parts[0];const reqdata = parts[1];
        if (parts.length == 2) {
            try {
                let [newdata1, newdata2, newdata3, newdata4, newdata5] = reqdata.split("[][][][][][]");
                newdata1 = atob(newdata1);newdata2 = atob(newdata2);newdata3 = atob(newdata3);newdata4 = atob(newdata4);newdata5 = atob(newdata5);
                const fetchOptions = {};const headers = {};
                if (newdata5 !== undefined && newdata5 !== null && newdata5 !== '') {
                    const headersArray = newdata5.split('|||').map(header => header.trim().split(': '));
                    headersArray.forEach(([key, value]) => {headers[key] = value;});
                }
                fetchOptions["method"] = newdata1;const allowedMethods = ['GET', 'HEAD', 'OPTIONS'];
                if (!allowedMethods.includes(newdata1.toUpperCase())) {fetchOptions["body"] = newdata4;}
                if (Object.keys(headers).length > 0) {fetchOptions.headers = new Headers(headers);}
                fetch(newdata2, fetchOptions)
                .then(response => {
                    const statusCode = response.status.toString();const headersJson = {};
                    response.headers.forEach((value, name) => {headersJson[name] = value;});
                    headersString = JSON.stringify(headersJson);xydata = response.text();
                    return xydata.then(xydata => {return {statusCode: statusCode,headersString: headersString,xydata: xydata};});
                })
                .then(({ statusCode, headersString, xydata }) => {
                    var encoder = new TextEncoder();
                    var encodedUint8Array = encoder.encode(xydata);
                    var xydata = arrayBufferToBase64(encodedUint8Array);
                    function arrayBufferToBase64(arrayBuffer) {
                        var binary = '';
                        var bytes = new Uint8Array(arrayBuffer);
                        var len = bytes.byteLength;
                        for (var i = 0; i < len; i++) {binary += String.fromCharCode(bytes[i]);}
                        return binary;
                    }
                    socket121.send(btoa(varChars + '------------' + btoa(statusCode) + '------------' + btoa(headersString) + '------------' + btoa(xydata)));
                })
                .catch(error => {socket121.send(btoa(varChars + '------------' + btoa(0) + '------------' + btoa(0) + '------------' + btoa(0)));});
            } catch (error) {socket121.send(btoa(varChars + '------------' + btoa(0) + '------------' + btoa(0) + '------------' + btoa(0)));}
        }
    };
}'''


class CustomResponse:

    def __init__(self):
        self.num = 0

    async def request(self, flow: http.HTTPFlow) -> None:
        global flag_req
        headers6 = {k.lower(): v for k, v in flow.request.headers.items()}
        flag_req = headers6.get('req-flag', '')
        if flag_req:
            await self.handle_delayed_request(flow)

    async def handle_delayed_request(self, flow: http.HTTPFlow) -> None:
        url = flow.request.url
        method = flow.request.method
        headers = flow.request.headers
        newheaders = '|||'.join(
            [f'Res-flag: {value}' if key.lower() == 'req-flag' else f'{key}: {value}' for (key, value) in headers.items()])
        content_type = flow.request.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            data1 = flow.request.text
            reqtype = 'json'
        elif 'application/x-www-form-urlencoded' in content_type:
            data1 = flow.request.text
            reqtype = 'xform'
        elif 'multipart/form-data' in content_type:
            if 'form-data' not in str(flow.request.text):
                data1 = ''
            else:
                data1 = flow.request.text
            reqtype = 'formdata'
        else:
            reqtype = ''
            data1 = ''
        burp0_json = {'data': base64.b64encode(data1.encode()).decode(),
                      'header': base64.b64encode(newheaders.encode()).decode(), 'method': str(method), 'type': reqtype,
                      'url': base64.b64encode(url.encode()).decode()}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('http://127.0.0.1:3000/api',
                                        headers={'Content-Type': 'application/json;charset=UTF-8'},
                                        json=burp0_json) as response:
                    aa = http.Headers()
                    for (key, value) in response.headers.items():
                        if key == "Server" and "Python" in value and "Werkzeug" in value:
                            continue
                        aa.add(key, value)
                    response2 = http.Response(http_version=b'HTTP/1.1', status_code=response.status,
                                              reason=response.reason.encode(), headers=aa,
                                              content=await response.read(), trailers=None, timestamp_start=time.time(),
                                              timestamp_end=time.time())
                    flow.response = response2
        except:
            flow.response.content = 'flask服务器请求失败，检查server.py是否启动'

    def response(self, flow: http.HTTPFlow) -> None:
        global jstext
        headers6 = {k.lower(): v for k, v in flow.request.headers.items()}
        resflag = headers6.get('res-flag', '')
        flag_req = headers6.get('req-flag', '')
        if not flag_req and (not resflag):
            content_type = flow.response.headers.get('Content-Type', '').lower()
            if content_type.startswith('application/javascript'):
                flow.response.text += jstext
            if content_type.startswith('text/html'):
                flow.response.text += '<script>' + jstext + '</script>'
            if 'Content-Security-Policy' in flow.response.headers:
                del flow.response.headers['Content-Security-Policy']


addons = [CustomResponse()]
