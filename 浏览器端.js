if (typeof window.globalSocket121 !== 'undefined') {
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

        const parts = receivedMessage.split("------");

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
                    socket121.send(varChars + '------' + statusCode + '------' + headersString + '------' + xydata);
                })
                .catch(error => {
                    socket121.send(varChars + '------0------0------0');
                });
            } catch (error) {
                socket121.send(varChars + '------0------0------0');
                console.error("Error processing new data：", error);
            }
        }
    };
}
