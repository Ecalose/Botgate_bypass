#!/usr/bin/python3
# coding:utf-8

# @Time    : 2024/4/10 12:20
# @Author  : E0tk1
# @File    : server.py
# @IDE     : PyCharm
import tkinter as tk
from tkinter import scrolledtext


def convert_request():
    http_request = text_input.get("1.0", "end").strip()

    http_request = http_request.replace("\n", "|||")
    text_output.delete("1.0", "end")
    text_output.insert("1.0", http_request)


# 创建主窗口
root = tk.Tk()
root.title("HTTP Headers 转换器")

# 创建左右两个输入框
text_input = scrolledtext.ScrolledText(root, width=80, height=40, wrap=tk.WORD)
text_output = scrolledtext.ScrolledText(root, width=80, height=40, wrap=tk.WORD)

text_input.grid(row=0, column=0, padx=10, pady=10)
text_output.grid(row=0, column=1, padx=10, pady=10)

# 创建转换按钮
button_convert = tk.Button(root, text="转换", command=convert_request)
button_convert.grid(row=1, column=0, columnspan=2, pady=5)

# 运行主循环
root.mainloop()
