[TOC]



# Botgate_bypass

简介：绕过瑞数waf的动态验证机制，实现请求包重放，可针对不同网站使用。

## 瑞数waf？

### 简介

瑞数下一代WAF，即WAAP平台，以独特的“动态安全”为核心技术，以Bot防护为核心功能，结合智能威胁检测技术、行为分析技术，提供传统Web安全防御能力的同时，更能将威胁提前止于攻击的漏洞探测和踩点阶段，轻松应对新兴和快速变化的Bots攻击、0day攻击、应用DDoS攻击和API安全防护。

### 判断瑞数waf网站

##### 1、页面首次访问状态码412，页面中带有随机目录和文件名的js

![image-20240412095824474](./assets/image-20240412095824474.png)

![image-20240412095746439](./assets/image-20240412095746439.png)

##### 2、访问请求和Cookie中带有动态加密的字符

![image-20240412095947665](./assets/image-20240412095947665.png)

##### 3、重发请求时会返回400状态码

![image-20240412102736154](./assets/image-20240412102736154.png)

## 工具使用

### 前置准备

```
python3环境
所需的第三方库（pip install -r requirements.txt）
注意：版本不能过低（会有未知BUG）
```

### 使用方式

#### 1、启动server程序

```
python server.py
或
start_server.bat
```

![image-20240412100213281](./assets/image-20240412100213281.png)

#### 2、执行客户端JS代码

在需要请求的网站上执行【浏览器端.js】中的代码，连接成功后server端会显示相关信息

（针对浏览器、小程序、微信浏览器、移动端、模拟器等环境，详见后面具体教程）

![image-20240412100413856](./assets/image-20240412100413856.png)

![image-20240412100508105](./assets/image-20240412100508105.png)

#### 3、调用程序进行重发请求

```
POST /api?data=参数五(json格式时) HTTP/1.1
Host: 127.0.0.1:3000
Content-Type: application/json;charset=UTF-8
Content-Length: 109

{"method": "参数一","url":  "参数二","type":"参数三","header":"参数四","data":"参数五"}
```

#### 4、参数详解：

##### 参数一：网站请求方法

```
可选值：
GET、POST
```

##### 参数二：网站URL

```
URL（例：https://www.baidu.com）
```

##### 参数三：请求的Content-Type类型

```
可选值：
xfrom			等同于application/x-www-form-urlencoded
json			等同于application/json	（注意：选该类型时，传参数五时需要在URL中传参，详见后面例子）
formdata		等同于multipart/form-data
```

##### 参数四（可选）：自定义header头信息

```
例子格式：
A: zxss|||B: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c|||C: pc
```

说明：可以使用附带工具【headers转可用格式.py】，将请求包内的特殊headers格式转换

注意1：不能带请求类型和URL部分

注意2：Host、Cookie、User-Agent等字段不可自定义，此处加上，后面请求也会被覆盖

![image-20240412102110273](./assets/image-20240412102110273.png)

##### 参数五：传输的数据

```
xfrom例子：
a=1&b=2&c=3
json例子：（传该类型参数时需要放在URL上）
{"a":"1","b":"2","c":"3"}
formdata例子：
a=1&b=2&c=3
```

### 使用案例

##### 普通GET请求

![image-20240412103024640](./assets/image-20240412103024640.png)

实际请求：

![image-20240412103911960](./assets/image-20240412103911960.png)

##### json格式的POST请求

![image-20240412103412478](./assets/image-20240412103412478.png)

实际请求：

![image-20240412103745227](./assets/image-20240412103745227.png)

##### xfrom格式的POST请求

![image-20240412103156012](./assets/image-20240412103156012.png)

实际请求：

![image-20240412104010323](./assets/image-20240412104010323.png)

##### formdata格式的请求

![image-20240412103339040](./assets/image-20240412103339040.png)

实际请求：

![image-20240412104128634](./assets/image-20240412104128634.png)

##### 带自定义Header头的 请求

![image-20240412103541368](./assets/image-20240412103541368.png)

实际请求：

![image-20240412104210108](./assets/image-20240412104210108.png)

### 不同访问环境的使用

##### 浏览器

1、油猴插件（建议）

![image-20240412104805558](./assets/image-20240412104805558.png)

2、手动在浏览器控制台执行js代码

##### 小程序、微信浏览器

1、如果访问网站有附带js请求或html请求，手动修改响应数据，将js代码放进去

2、使用WeChatOpenDevTools开启调试，在控制台执行js代码

3、Burp上游增加一层minmproxy，将每次的js或html响应中增加js代码（预计下版本增加脚本）

##### 模拟器

1、如果访问网站有附带js请求或html请求，手动修改响应数据，将js代码放进去

2、使用WeChatOpenDevTools开启调试，在控制台执行js代码

3、Burp上游增加一层minmproxy，将每次的js或html响应中增加js代码（预计下版本增加脚本）

注意：非本机环境需要将【浏览器端.js】中的第一行地址修改

### 可能遇到的问题

##### 1、遇到站点csp策略限制

![image-20240412110155182](./assets/image-20240412110155182.png)

在Burp上把csp策略替换掉

![image-20240412110215174](./assets/image-20240412110215174.png)