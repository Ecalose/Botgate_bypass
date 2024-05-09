* [Botgate_bypass](#botgate_bypass)
  * [瑞数waf？](#瑞数waf)
    * [简介](#简介)
    * [判断瑞数waf网站](#判断瑞数waf网站)
  * [工具使用](#工具使用)
    * [前置准备](#前置准备)
    * [使用方式](#使用方式)
      * [1、启动server程序](#1启动server程序)
      * [2、执行mitmdump脚本](#2执行mitmdump脚本)
      * [3、进行重发请求](#3进行重发请求)
* [注意事项](#注意事项)
* [更新日志](#更新日志)
* [交流群](#交流群)

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

装完三方库后，需要安装C:\Users\【用户名】\mitmproxy目录中mitmproxy-ca-cert.cer证书

### 使用方式

#### 1、启动server程序

```
python server.py
或
start_server.bat
```

![image-20240412100213281](./assets/image-20240412100213281.png)

#### 2、执行mitmdump脚本

##### 使用mitmdump自动添加js（适合所有网站环境）

1、如访问网站非本机环境时，需要将ws通信地址修改成本机地址

![image-20240416105052721](./assets/image-20240416105052721.png)

2、启动mitmdump

```
mitmdump -p 8081 -s mitmdump.py
或
mitmdump_start.bat
```

3、Burp添加上游代理

注意：不要只填*，会导致非目标网站执行js，影响正常使用。

![image-20240415140549082](./assets/image-20240415140549082.png)

![image-20240412100508105](./assets/image-20240412100508105.png)

#### 3、进行重发请求

```
直接使用原请求包，header头中添加Req-flag: 1
```

例：

![image-20240416122446746](./assets/image-20240416122446746.png)

# 注意事项

```
1.默认网站响应超时时间2s
2.上游代理需指定域名或IP
3.批量请求时线程不要太大
```

如果遇到访问失败等情况

![image-20240509111851676](./assets/image-20240509111851676.png)

可以使用mitmdump-debug_start.bat，重发请求，到浏览器控制台查看报错，如果是代码问题可以提issues。

# 更新日志

##### 2024年4月25日

优化代码，解决已知BUG，更新v2.1版本

##### 2024年4月16日

更新v2.0版本

##### 2024年4月15日

修复已知问题

##### 2024年4月12日

v1.0版本发布

# 交流群

关注公众号【Tokaye安全】，发送加群。
